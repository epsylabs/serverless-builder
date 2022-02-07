import io
from collections import OrderedDict
from pathlib import Path
from typing import Union

import yaml

from serverless.service.configuration import Configuration
from serverless.service.functions import FunctionManager
from serverless.service.package import Package
from serverless.service.plugins import PluginsManager
from serverless.service.resources import ResourceManager
from serverless.service.types import Identifier, Provider, YamlOrderedDict


class Builder:
    def __init__(self, service):
        self.service = service
        self.function = service.provider.function_builder


class PreSetAttributesBuilder(Builder):
    def __init__(self, service, preset):
        super().__init__(service)
        self._preset = preset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __getattr__(self, item):
        def wrapper(*args, **kwargs):
            return getattr(self.function, item)(*args, **{**kwargs, **self._preset})

        return wrapper


class Service(OrderedDict, yaml.YAMLObject):
    yaml_tag = "!Service"

    def __init__(
        self, name: str, description: str, provider: Provider, config=None, custom: Union[dict, None] = None, /, **kwds
    ):
        super().__init__(**kwds)

        self.service = Identifier(name)
        self.package = Package(["!./**/**", f"{self.service.snake}/**"])
        self.variablesResolutionMode = 20210326
        self.custom = YamlOrderedDict(vars="${file(./variables.yml):${sls:stage}}", **(custom or {}))

        self.config = config if config else Configuration()

        provider.configure(self)
        self.provider = provider

        self.plugins = PluginsManager(self)
        self.functions = FunctionManager(self)
        self.resources = ResourceManager(self, description)

        self.builder = Builder(self)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.builder = Builder(self)
        return self

    def preset(self, **kwargs):
        self.builder = PreSetAttributesBuilder(self, kwargs)

        return self.builder

    def enable(self, feature):
        feature.enable(self)

    def render(self, output=None):
        if output:
            output.write(str(self))
            return

        import __main__ as main

        with open(Path(main.__file__).stem, "w+") as f:
            f.write(str(self))

    def __str__(self):
        buf = io.StringIO()
        yaml.dump(self, buf, sort_keys=False, indent=2)
        buf.seek(0)
        tmp_buf = io.StringIO()

        for line in buf:
            if line.split(":")[0] in ("provider", "plugins", "package", "custom", "functions", "resources", "vars"):
                tmp_buf.write("\n")

            tmp_buf.write(line)
        tmp_buf.seek(0)

        return tmp_buf.read()

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("builder", None)
        data.pop("config", None)
        data.pop("function_builder", None)
        return dumper.represent_dict(data)
