# This file is part of the confdoggo project
# Feel free to use it as you wish

import confdoggo
import http.server
from datetime import datetime


class Settings(confdoggo.Settings):
    class _(confdoggo.Settings):
        host: str = "localhost"
        port: int = 8080

    server = _()

    class _(confdoggo.Settings):
        x: int = 123

    client = _()

    reload_on_changes = True
    scheduled_shutdown: datetime = None


settings = confdoggo.go_catch(
    Settings,
    [
        "file://./simple.json",  # a local file
        # 'ftp://192.168.1.1/folder/file.json',  # a remote file
        # 'https://192.168.1.2/folder/file.ini',  # another remote file
    ],
)

print(settings)

server = http.server.HTTPServer(
    (settings.server.host, settings.server.port), http.server.BaseHTTPRequestHandler
)
