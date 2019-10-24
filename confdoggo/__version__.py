#!/usr/bin/python3

# Copyright (C) 2019  The confdoggo Authors
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


class Version:
    major = 0
    minor = 1
    patch = 0
    notes = 'alpha'
    string = '.'.join((str(major), str(minor), str(patch))) + notes


__title__ = 'confdoggo'
__description__ = 'Your personal configuration doggo.'
__url__ = 'https://github.com/dpdani/confdoggo'
__version__ = Version()
__author__ = 'Daniele Parmeggiani'
__author_email__ = 'git@danieleparmeggiani.me'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2019 Daniele Parmeggiani'

