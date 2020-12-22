#  Copyright (C) 2020  The confdoggo Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import abc
from ..utils import DoggoException, Configuration


class BaseFrontend(abc.ABC):
    @abc.abstractmethod
    def parse(self, config: Configuration):
        pass


class UnknownFrontend(DoggoException):
    def __init__(self, mime_type):
        self.mime_type = mime_type
        super().__init__(f"for mime type '{self.mime_type}'.")


def json_frontend():
    from . import json

    return json.JsonFrontend()


def yaml_frontend():
    from . import yaml

    return yaml.YamlFrontend()


# def doggo_frontend():
#     from . import doggo
#     return doggo.ConfdoggoFrontend()
#
# def toml_frontend():
#     from . import toml
#     return toml.TomlFrontend()
#
# def ini_frontend():
#     from . import ini
#     return ini.IniFrontend()


frontends_registry = {
    # mime type -> frontend class
    "application/json": json_frontend,
    "application/x-yaml": yaml_frontend,
    # TODO
    # 'application/confdoggo': doggo_frontend,
    # 'application/toml': toml_frontend,
    # 'application/ini': ini_frontend,
}


def get_frontend(mime_type: str):
    try:
        return frontends_registry[mime_type]()
    except KeyError:
        raise UnknownFrontend(mime_type)
