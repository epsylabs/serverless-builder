import abc
from collections import OrderedDict

import stringcase
import yaml


class YamlOrderedDict(OrderedDict, yaml.YAMLObject):
    yaml_tag = "!YamlOrderedDict"

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data)


class Identifier(yaml.YAMLObject):
    yaml_tag = "Identifier"

    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier

    @property
    def camel(self):
        return stringcase.camelcase(self.identifier)

    @property
    def pascal(self):
        return stringcase.pascalcase(self.identifier)

    @property
    def snake(self):
        return stringcase.snakecase(self.identifier)

    @property
    def spinal(self):
        return stringcase.spinalcase(self.identifier)

    def __str__(self):
        return self.identifier

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_str(str(data.identifier))


class ProviderMetadata(type(YamlOrderedDict), type(abc.ABC)):
    pass


class Provider(YamlOrderedDict, abc.ABC, metaclass=ProviderMetadata):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)


class Feature(abc.ABC):
    @abc.abstractmethod
    def enable(self, service):
        pass


class PluginMetadata(type(YamlOrderedDict), type(abc.ABC)):
    pass


class Plugin(YamlOrderedDict, abc.ABC, metaclass=PluginMetadata):
    @abc.abstractmethod
    def enable(self, service):
        pass
