# confdoggo 🐶

Define your builtin settings:

```python
class MySettings(confdoggo.Settings):
    class _(confdoggo.Settings):
        host: str = "localhost"
        port: int = 8080
    server = _()

    class _(confdoggo.Settings):
        x: int = 42
    client = _()

    reload_on_changes = True
    scheduled_shutdown: datetime = None
```

Let confdoggo catch the configuration files, and run extensible type checking:

```python
settings = confdoggo.go_catch(
    MySettings,
    [
        'file://./simple.json',  # a local file
        Path('.') / 'another_one.yaml',  # another local file
        'ftp://192.168.1.1/folder/file.json',  # a remote file
        'https://192.168.1.2/folder/file.ini',  # another remote file
    ],
)
```
Note: order matters! Configurations that have a higher index have higher importance.

Access configuration easily:

```python
assert settings.server.port == 8080 
```

See a full example [here](./examples/simple.py).


## Install

```bash
$ pip install confdoggo
```


## Under development

This project is under development: expect breaking changes!
