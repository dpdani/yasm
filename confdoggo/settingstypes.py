#!/usr/bin/python3

# Copyright (C) 2017  The confdoggo Authors
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


import re
import datetime
from abc import abstractmethod

from . import DoggoException


class InvalidName(DoggoException):
    pass


class NoneValueException(DoggoException):
    def __init__(self, item_name):
        self.item_name = item_name
        super().__init__(f'self.value_ is None. ({item_name})')


class ConversionException(DoggoException):
    def __init__(self, value, data_type):
        self.value = value
        self.data_type = data_type
        super().__init__(f"couldn't convert '{value}' to {data_type.__class__.__name__}.")


class SettingsType(object):
    """SettingsType is the abstract base class for all DataTypes in confdoggo,
    may they be primitive or user-defined.
    Since this class's __dict__ is used for evaluating sub-elements of
    a settings's tree, its methods and attributes often have a trailing '_'.

    SettingsType.is_tree_ is used to determine whether this SettingsType can
    contain sub-elements, in which case, SettingsType.value_ is expected to
    be a dict.
    """
    valid_name_ = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    is_tree_ = False

    def __init__(self, name, value=None):
        self.name_ = None
        if name is None:  # temporary name
            return
        if re.match(self.valid_name_, name) is None:
            raise InvalidName(
                f"name '{name}' is not acceptable. See confdoggo.types.SettingsType.valid_name_."
            )
        try:
            self.__getattribute__(name)
        except AttributeError:
            pass
        else:
            raise InvalidName(f"name '{name}' is reserved.")
        self.name_ = name
        self.value_ = value

    @abstractmethod
    def convert_(self):
        """This method is used to convert the parsed self.value_
        into the value that is meaningful by the application.
        For instance, Datetime('2017-01-01') may be parsed and needs to be
        converted to the appropriate datetime instance."""
        pass

    def convert_pre_(self):
        if self.value_ is None:
            raise NoneValueException(self.name_)
        self.convert_()

    def __repr__(self):
        return f"<{self.__class__.__name__} `{self.name_}`: {self.value_}>"


class String(SettingsType):
    def convert_(self):
        if type(self.value_) == str:
            return
        else:
            raise ConversionException(self.value_, self)


class Integer(SettingsType):
    def convert_(self):
        value_type = type(self.value_)
        if value_type == int:
            return
        elif value_type == str:
            try:
                self.value_ = int(self.value_)
            except ValueError:
                raise ConversionException(self.value_, self)
        else:
            raise ConversionException(self.value_, self)


class Float(SettingsType):
    def convert_(self):
        value_type = type(self.value_)
        if value_type == float:
            return
        elif value_type == int:
            self.value_ = float(self.value_)
            return
        elif value_type == str:
            try:
                self.value_ = float(self.value_)
            except ValueError as exc:
                raise ConversionException(self.value_, self) from exc
        else:
            raise ConversionException(self.value_, self)


class Boolean(SettingsType):
    trues_ = ('True', 'true', 'yes', 'on', '1')
    falses_ = ('False', 'false', 'no', 'off', '0')

    def convert_(self):
        value_type = type(self.value_)
        if value_type == bool:
            return
        elif value_type == str:
            if self.value_ in self.trues_:
                self.value_ = True
                return
            elif self.value_ in self.falses_:
                self.value_ = False
                return
            else:
                raise ConversionException(self.value_, self)
        elif value_type == int:
            if self.value_ == 1:
                self.value_ = True
                return
            elif self.value_ == 0:
                self.value_ = False
                return
            else:
                raise ConversionException(self.value_, self)
        else:
            raise ConversionException(self.value_, self)


class Timedelta(SettingsType):
    timedelta_parse_string_ = '%M:%S'

    def convert_(self):
        if isinstance(self.value_, datetime.timedelta):
            return
        elif type(self.value_) == str:
            try:
                tmp = datetime.datetime.strptime(self.value_, self.timedelta_parse_string_)
                self.value_ = datetime.timedelta(minutes=tmp.minute, seconds=tmp.second)
            except (ValueError, TypeError) as exc:
                raise ConversionException(self.value_, self) from exc


class Datetime(SettingsType):
    datetime_parse_string_ = ''

    def convert_(self):
        # TODO
        pass


class List(SettingsType):
    # TODO
    pass


class Tree(SettingsType):
    is_tree_ = True

    def convert_(self):
        if type(self.value_) != dict:
            raise ConversionException(self.value_, self)
        for key, child in self.value_.items():
            if type(child) == dict:
                child_tree = Tree(key)
                child_tree.value_ = child
                self.value_[key] = child_tree
                child = child_tree
            child.convert_pre_()
        return

    def __getattr__(self, item):
        if self.value_ is not None:
            if item in self.value_.keys():
                return self.value_[item]

    def __contains__(self, item):
        if self.value_ is None:
            raise NoneValueException(self.name_)
        return item in self.value_.keys()

    def __len__(self):
        if self.value_ is None:
            raise NoneValueException(self.name_)
        return len(self.value_.keys())
