import io
import sys
from collections import OrderedDict

import yaml

from serverless.aws.iam import IAMManager
from serverless.aws.provider import FunctionBuilder
from serverless.service.functions import FunctionManager
from serverless.service.package import Package
from serverless.service.plugins import PluginsManager
from serverless.service.resources import ResourceManager
from serverless.service.types import Identifier, Provider, YamlOrderedDict


class Service(OrderedDict, yaml.YAMLObject):
    yaml_tag = "!Service"

    def __init__(self, name: str, description: str, provider: Provider, /, **kwds):
        super().__init__(**kwds)
        self.service = Identifier(name)
        self.package = Package(["!./**/**", f"{name}/**"])
        self.provider = provider
        self.provider.iam = IAMManager(self)
        self.provider.functions = FunctionBuilder(self)
        self.custom = YamlOrderedDict(stage="${opt:stage, self:provider.stage}")
        self.plugins = PluginsManager(self)
        self.functions = FunctionManager(self)
        self.resources = ResourceManager(self, description)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)

    def enable(self, feature):
        feature.enable(self)

    def render(self, to=None):
        out = to or sys.stdout
        out.write(str(self))

    def __str__(self):
        buf = io.StringIO()
        yaml.dump(self, buf, sort_keys=False, indent=2)
        buf.seek(0)

        return buf.read()

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data)
