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


class BaseClient(abc.ABC):
    @abc.abstractmethod
    def go_catch(self, config: Configuration, url: str) -> None:
        pass


class UnknownClient(DoggoException):
    def __init__(self, client_name):
        self.client_name = client_name
        super().__init__(f"for URL protocol '{self.client_name}'.")


def fs_client():
    from . import fs

    return fs.FileSystemClient()


clients_registry = {
    "file": fs_client,
    # TODO
    # 'http': ['http', 'HttpClient'],
    # 'https': ['https', 'HttpsClient'],
    # 'ssh': ['ssh', 'SshClient'],
    # 'ftp': ['ftp', 'FtpClient'],
}


def get_client(client_type: str):
    try:
        return clients_registry[client_type]()
    except KeyError:
        raise UnknownClient(client_type)
