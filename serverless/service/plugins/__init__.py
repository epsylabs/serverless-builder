import yaml

from serverless.service.types import Plugin


class PluginsManager(yaml.YAMLObject):
    yaml_tag = "!Plugins"

    def __init__(self, service):
        super().__init__()
        self._service = service
        self._plugins = []

    def add(self, plugin: Plugin):
        plugin.enable(self._service)
        self._plugins.append(plugin)

    def all(self):
        return self._plugins

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_list([plugin.name for plugin in data.all()])
