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

from dataclasses import dataclass


@dataclass
class Configuration:
    url: str = None
    content: str = None
    mime_type: str = None
    parsed_content: dict = None
    watcher = None  # : watchers.BaseWatcher


class DoggoException(Exception):
    pass


class MissingLibraryException(DoggoException):
    def __init__(self, library, extras):
        super().__init__(
            f"missing library '{library}'. "
            f"To install all the necessary components, "
            f"run `pip install confdoggo[{extras}]`."
        )
