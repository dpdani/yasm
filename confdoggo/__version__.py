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

from functools import total_ordering


@total_ordering
class Version:
    major = 0
    minor = 1
    patch = 0
    notes = "alpha"

    @property
    def as_string(self):
        return ".".join((str(self.major), str(self.minor), str(self.patch))) + (
            ("-" + self.notes) if self.notes else ""
        )

    @property
    def as_tuple(self):
        if self.notes:
            return self.major, self.minor, self.patch, self.notes
        else:
            return self.major, self.minor, self.patch

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.as_tuple < other.as_tuple
        if isinstance(other, tuple):
            return self.as_tuple < other
        raise TypeError("not supported.")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.as_tuple == other.as_tuple
        if isinstance(other, tuple):
            return self.as_tuple == other
        raise TypeError("not supported.")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.as_string}>"

    def __str__(self):
        return self.as_string


__title__ = "confdoggo"
__description__ = "Your personal configuration doggo."
__url__ = "https://github.com/dpdani/confdoggo"
__version__ = Version()
__author__ = "Daniele Parmeggiani"
__author_email__ = "git@danieleparmeggiani.me"
__author_github__ = "dpdani"
__license__ = "GPLv3"
__copyright__ = "Copyright 2020 Daniele Parmeggiani"


__all__ = [
    "__title__",
    "__description__",
    "__url__",
    "__version__",
    "__author__",
    "__author_email__",
    "__author_github__",
    "__license__",
    "__copyright__",
]
