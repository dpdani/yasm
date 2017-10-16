#!/usr/bin/python3
#
# Copyright (C) 2017  The yasm Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import datetime
import enum
import re

valid_item_name = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
timedelta_parse_string = '%M:%S'


class YasmException(Exception):
    pass


class UndefinedValueException(YasmException):
    def __init__(self):
        super().__init__('self.value needs to be defined before converting it.')


class ConversionException(YasmException):
    def __init__(self, value, value_type):
        super().__init__("couldn't convert '{}' to {}.".format(value, value_type))


class UnknownSettingException(YasmException):
    def __init__(self, setting_path):
        self.setting_path = setting_path
        super().__init__("defined setting '{}' is unknown.".format(setting_path))


class InconsistentSettingTypeException(YasmException):
    def __init__(self, setting_path, should_be, got):
        self.setting_path = setting_path
        self.should_be = should_be
        self.got = got
        super().__init__("setting type for '{}' should be {}. Got: {}.".format(setting_path, should_be, got))


class SettingsTypes(enum.Enum):
    unknown = -1
    string = 0  # need no conversion
    integer = 1  # need no conversion
    boolean = 2  # need no conversion
    timedelta = 3
    settings_item = 4
    list = 5  # need no conversion


class SettingsItem:
    def __init__(self, name, value_type):
        if type(name) != str:
            raise TypeError('argument name must be a string.')
        if not isinstance(value_type, SettingsTypes):
            raise TypeError('argument value_types must be a SettingsTypes instance.')
        if re.match(valid_item_name, name) is None:
            raise ValueError('settings item name is not acceptable. See tBB.settings.valid_item_name.')
        else:
            try:
                self.__getattribute__(name)
            except AttributeError:
                pass
            else:
                raise ValueError('settings item name is not acceptable. Name reserved.')
        self.name = name
        self.value = None
        self.value_type = value_type

    def convert(self):
        if self.value is None:
            raise UndefinedValueException()
        # static conversions: basically, only do type checking
        if self.value_type == SettingsTypes.string:
            if type(self.value) != str:
                raise ConversionException(self.value, self.value_type)
        elif self.value_type == SettingsTypes.integer:
            if type(self.value) != int:
                raise ConversionException(self.value, self.value_type)
        elif self.value_type == SettingsTypes.boolean:
            if type(self.value) != bool:
                raise ConversionException(self.value, self.value_type)
        # complex conversions
        elif self.value_type == SettingsTypes.timedelta:
            self.value = self.convert_to_timedelta(self.value)
        elif self.value_type == SettingsTypes.settings_item:
            self.value = self.convert_to_settings_item(self.value)
        elif self.value_type == SettingsTypes.unknown:  # make a guess on what it could be
            if type(self.value) == int:
                self.value_type = SettingsTypes.integer
            elif type(self.value) == bool:
                self.value_type = SettingsTypes.boolean
            elif type(self.value) == list:
                self.value_type = SettingsTypes.list
            elif type(self.value) == dict:
                try:
                    self.value = self.convert_to_settings_item(self.value)
                except ConversionException as exc:
                    raise exc
                else:
                    self.value_type = SettingsTypes.settings_item
            elif type(self.value) == str:
                try:
                    self.value = self.convert_to_timedelta(self.value)
                except ConversionException:
                    self.value_type = SettingsTypes.string
                else:
                    self.value_type = SettingsTypes.timedelta

    @staticmethod
    def convert_to_timedelta(value):
        try:
            tmp = datetime.datetime.strptime(value, timedelta_parse_string)
            return datetime.timedelta(minutes=tmp.minute, seconds=tmp.second)
        except (ValueError, TypeError) as exc:
            raise ConversionException(value, SettingsTypes.timedelta) from exc

    @staticmethod
    def convert_to_settings_item(value):
        if type(value) != dict:
            raise ConversionException(value, SettingsTypes.settings_item)
        children = {}
        for name, elem in value.items():
            new_item = SettingsItem(name=name, value_type=SettingsTypes.unknown)
            new_item.value = elem
            children[name] = new_item
        for child in children.values():
            child.convert()
        return children

    def __getattr__(self, item):
        try:
            return self.__getattribute__(item)
        except AttributeError as exc:
            if self.value_type == SettingsTypes.settings_item and self.value is not None:
                if item in self.value.keys():
                    return self.value[item]
                else:
                    raise exc

    def __repr__(self):
        return "<{} '{}' ({})>".format(self.__class__.__name__, self.name, self.value_type)


class Settings:
    def __init__(self, tree):
        if not isinstance(tree, SettingsItem):
            raise TypeError("expected SettingsItem instance for argument tree. Got: '{}'.".format(tree))
        self.tree = tree

    def update(self, new_tree, scope=''):
        if not isinstance(new_tree, SettingsItem):
            raise TypeError("expected SettingsItem instance for argument tree. "
                            "Got: '{}'.".format(new_tree))
        if type(new_tree.value) != dict:
            walked_path = 'self.tree'
            try:
                setting = self.tree
                for selector in scope.split('.')[1:]:
                    walked_path += '.' + selector
                    setting = getattr(setting, selector)
            except AttributeError:
                raise UnknownSettingException(walked_path)
            else:
                if setting.value_type != new_tree.value_type:
                    raise InconsistentSettingTypeException(scope, setting.value_type,
                                                           new_tree.value_type)
                setting.value = new_tree.value
        else:
            for name in new_tree.value:
                if new_tree.value_type == SettingsTypes.settings_item:
                    self.update(new_tree.value[name], scope=self.tree.name+scope+'.'+name)
                else:
                    raise TypeError("expected iterators inside new_tree to be SettingsTypes.settings_item. "
                                    "Got: {}".format(new_tree.value_type))

    @staticmethod
    def parse(json_data, name='toplevel'):
        tree = SettingsItem(name=name, value_type=SettingsTypes.settings_item)
        tree.value = json_data
        tree.convert()
        return tree

    def __getattr__(self, item):
        return self.tree.__getattr__(item)
