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

import os
import threading
from . import BaseWatcher


try:
    import watchdog
    import watchdog.observers
    import watchdog.events

    has_watchdog = True
except ImportError:
    has_watchdog = False


class FileSystemOSWatcher(BaseWatcher):
    """ Dependant on available OS functionality. """

    def __init__(self, url, callback):
        super().__init__(url, callback)
        self.observer = watchdog.observers.Observer()
        self.event_handler = watchdog.events.FileModifiedEvent(self.path)
        self.event_handler.dispatch = lambda _: self.callback()
        self.observer.schedule(self.event_handler, self.path, recursive=False)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class FileSystemPollWatcher(BaseWatcher):
    def __init__(self, url, callback, polling_interval=5):
        self.polling_interval = polling_interval
        self.closing = threading.Event()
        self.thread = threading.Thread(target=self.run)
        super().__init__(url, callback)

    def start(self):
        self.thread.start()

    def run(self):
        last_modified = os.path.getmtime(self.path)
        while not self.closing.is_set():
            try:
                # print('checking', self.path, last_modified, os.path.getmtime(self.path))
                if os.path.getmtime(self.path) != last_modified:
                    # print('callback')
                    self.callback()
                    last_modified = os.path.getmtime(self.path)
            except OSError:
                # file no longer exists or is inaccessible
                self.callback()
                break
            self.closing.wait(self.polling_interval)

    def stop(self):
        self.closing.set()
        self.thread.join()


def get_watcher(url, callback, polling_interval=5):
    if has_watchdog:
        return FileSystemOSWatcher(url, callback)
    else:
        return FileSystemPollWatcher(url, callback, polling_interval)
