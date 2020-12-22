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
from typing import Callable
from ..utils import DoggoException


class BaseWatcher(abc.ABC):
    def __init__(self, url: str, callback: Callable):
        self.url = url
        _, self.path = self.url.split("://")
        self.callback = callback

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass


class UnknownWatcher(DoggoException):
    def __init__(self, watcher_name):
        self.watcher_name = watcher_name
        super().__init__(f"for URL protocol '{self.watcher_name}'.")


def fs_watcher():
    from . import fs

    return fs.get_watcher


watchers_registry = {
    "file": fs_watcher,
    # TODO
    # 'http': ['http', 'HttpClient'],
    # 'https': ['https', 'HttpsClient'],
    # 'ftp': ['ftp', 'FtpClient'],
}


def get_watcher(watcher_type: str):
    try:
        return watchers_registry[watcher_type]()
    except KeyError:
        raise UnknownWatcher(watcher_type)
