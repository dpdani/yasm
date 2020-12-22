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
from pathlib import Path

import confdoggo
import time


class MySettings(confdoggo.Settings):
    spam: int
    cheese: bool = True


settings = confdoggo.go_catch(MySettings, [Path(".") / "watchers.yaml"], watch=True)

try:
    while True:
        print(settings)
        time.sleep(1)
except KeyboardInterrupt:
    confdoggo.shutdown_watchers()
