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


from . import settingstypes


class DoggoException(Exception):
    pass


class UnknownSettingException(DoggoException):
    def __init__(self, setting_path):
        self.setting_path = setting_path
        super().__init__(f"defined setting '{setting_path}' is unknown.")


class InconsistentSettingTypeException(DoggoException):
    def __init__(self, setting_path, should_be, got):
        self.setting_path = setting_path
        self.should_be = should_be
        self.got = got
        super().__init__(f"setting type for '{setting_path}' should be {should_be}. Got: {got}.")


class Settings:
    def __init__(self, tree):
        if type(tree) == dict:
            tree = self.parse(tree)
        if not isinstance(tree, settingstypes.Tree):
            raise TypeError(f"expected Tree instance for argument tree. Got: '{tree}'.")
        self.tree = tree

    def update(self, new_tree, scope=''):
        if not isinstance(new_tree, settingstypes.SettingsType):
            raise TypeError(f"expected SettingsType instance for argument new_tree. Got: '{new_tree}'.")
        if type(new_tree.value_) != dict:
            walked_path = 'self.tree'
            try:
                setting = self.tree
                for selector in scope.split('.')[1:]:
                    walked_path += '.' + selector
                    setting = getattr(setting, selector)
            except AttributeError:
                raise UnknownSettingException(walked_path)
            else:
                if setting.__class__ != new_tree.__class__:
                    raise InconsistentSettingTypeException(scope, setting.__class__,
                                                           new_tree.__class__)
                setting.value_ = new_tree.value_
        else:
            for name in new_tree.value_:
                if isinstance(new_tree, settingstypes.SettingsType):
                    self.update(new_tree.value_[name], scope=self.tree.name_ + scope + '.' + name)
                else:
                    raise TypeError(f"expected iterators inside new_tree to be instances of Tree. "
                                    "Got: '{new_tree.__class__.__name__}'.")

    @staticmethod
    def parse(data, name='top-level'):
        tree = settingstypes.Tree(name, data)
        tree.convert_pre_()
        return tree

    def __getattr__(self, item):
        return self.tree.__getattr__(item)


def make_settings(root, name='top-level'):
    root = Settings.parse(root)
    settings = Settings(root)
    return settings
