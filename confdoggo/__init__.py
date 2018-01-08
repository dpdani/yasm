#!/usr/bin/python3
#
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


__version__ = (1,0,0, 'pre-alpha')
__authors__ = (
    'Daniele Parmeggiani, <dani.parmeggiani@gmail.com> | @dpdani on GitHub',
)


class DoggoException(Exception):
    pass

from .core import *
from .settingstypes import *
