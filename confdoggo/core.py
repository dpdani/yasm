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

from __future__ import annotations


from .utils import Configuration, DoggoException
from . import clients, frontends, watchers
import pydantic
from typing import Iterable, Type, Union
from pathlib import Path
import functools
import collections


class Settings(pydantic.BaseModel):
    def update(self, obj: dict):
        def _setter(obj, dictionary):
            for key in dictionary:
                if isinstance(key, dict):
                    _setter(getattr(self, dictionary[key]), dictionary[key])
                else:
                    if getattr(obj, key) != dictionary[key]:
                        # avoid triggering change events
                        # when unnecessary
                        setattr(obj, key, dictionary[key])

        _setter(self, obj)


class RootSettingsManager:
    def __init__(
        self,
        root_settings: Settings,
        configurations: collections.OrderedDict[str, Configuration],
    ):
        self.root_settings = root_settings
        self.configurations = configurations

    def subsequent_configurations(self, config_url: str):
        found = False
        for url in self.configurations:
            if found:
                yield url
            if url == config_url:
                found = True

    def watch_callback(self, configuration_url):
        try:
            new, _ = _go_catch_one(self.root_settings.__class__, configuration_url)
        except pydantic.ValidationError as e:
            print(
                f"Ignoring validation errors encountered while updating "
                f"configuration from '{configuration_url}':\n"
                f"{str(e)}\n"
                f"Skipping update."
            )
            return
        for config in self.subsequent_configurations(configuration_url):
            config = self.configurations[config]
            new_settings, _ = _go_catch_one(self.root_settings.__class__, config.url)
            new.update(new_settings.dict())
        self.root_settings.update(new.dict())

    def register_watchers(self):
        for url in self.configurations:
            self.register_watcher_for_url(url)

    def register_watcher_for_url(self, url: str):
        config = self.configurations[url]
        watcher_type, _ = url.split("://")
        watcher_class = watchers.get_watcher(watcher_type)
        config.watcher = watcher_class(url, functools.partial(self.watch_callback, url))
        config.watcher.start()

    def shutdown_watchers(self):
        for config in self.configurations.values():
            if config.watcher:
                config.watcher.stop()


roots_registry: dict[Type[Settings], RootSettingsManager] = {}


def shutdown_watchers():
    for manager in roots_registry.values():
        manager.shutdown_watchers()


class NoConfigurationsException(DoggoException):
    def __init__(self):
        super().__init__("No configuration URLs supplied.")


def go_catch(
    settings_class: Type[Settings],
    configurations: Iterable[Union[str, Path]],
    watch=False,
):
    settings = None
    config_objects = collections.OrderedDict()
    for config_url in configurations:
        if isinstance(config_url, Path):
            config_url = "file://" + str(config_url)
        else:
            try:
                client_type, url = config_url.split("://")
            except ValueError:
                # when no protocol is specified the file://
                # protocol is assumed
                config_url = "file://" + config_url
        settings, config = _go_catch_one(settings_class, config_url)
        config_objects[config_url] = config
    if settings is None:
        raise NoConfigurationsException()
    manager = RootSettingsManager(settings, config_objects)
    roots_registry[settings_class] = manager
    if watch:
        manager.register_watchers()
    return settings


def _go_catch_one(settings: Type[Settings], configuration_url: str):
    client_type, url = configuration_url.split("://")
    client = clients.get_client(client_type)
    config = Configuration(url=configuration_url)
    client.go_catch(config, url)
    frontend = frontends.get_frontend(config.mime_type)
    frontend.parse(config)
    return settings.parse_obj(config.parsed_content), config


__all__ = [
    "Settings",
    "shutdown_watchers",
    "NoConfigurationsException",
    "go_catch",
]
