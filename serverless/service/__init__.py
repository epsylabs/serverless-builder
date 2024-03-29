import io
import os
import shutil
from collections import OrderedDict
from pathlib import Path
from typing import Optional

import yaml

from serverless.aws.features.stepfunctions import StepFunctions
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
        self,
        name: str,
        description: str,
        provider: Provider,
        config: Optional[Configuration] = None,
        custom: Optional[dict] = None,
        regions=None,
        **kwds,
    ):
        super().__init__(**kwds)

        self.service = Identifier(name)
        self.package = Package(["!./**/**", f"{self.service.snake}/**"])
        self.variablesResolutionMode = 20210326
        if config.advanced_variables:
            src = os.path.dirname(__file__) + "/../static/config.js"
            dst = os.getcwd() + "/config.js"
            shutil.copyfile(src, dst)

            self.custom = YamlOrderedDict(
                var_files=[
                    "${file(./variables.yml):${sls:stage}}",
                    "${file(./variables_${env:APP_NAME}.yml):${sls:stage}}",
                ],
                vars="${file(./config.js)}",
                **(custom or {}),
            )
        else:
            self.custom = YamlOrderedDict(vars="${file(./variables.yml):${sls:stage}}", **(custom or {}))
        self.config = config or Configuration()
        self.regions = regions

        provider.configure(self)
        self.provider = provider

        self.plugins = PluginsManager(self)
        self.functions = FunctionManager(self)
        self.resources = ResourceManager(self, description)

        self.builder = Builder(self)
        self.stepFunctions = StepFunctions(self)
        self.features = []

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
        self.features.append(feature)
        feature.enable(self)

    def render(self, output=None, auto_generated_warning=True):
        if "SERVERLESS_BUILDER_DISABLE_RENDER" in os.environ:
            return

        import __main__ as main

        output = output if output else open(Path(main.__file__).stem, "w+")
        content = (
            "# DO NOT edit this file directly, it was generated based on serverless.yml.py\n\n" + str(self)
            if auto_generated_warning
            else str(self)
        )

        output.write(content)

    def __str__(self):
        buf = io.StringIO()
        yaml.dump(self, buf, sort_keys=False, indent=2, width=1000)
        buf.seek(0)
        tmp_buf = io.StringIO()

        for line in buf:
            if line.split(":")[0] in ("provider", "plugins", "package", "custom", "functions", "resources", "vars"):
                tmp_buf.write("\n")

            tmp_buf.write(line)
        tmp_buf.seek(0)

        return tmp_buf.read()

    def has(self, feature):
        return len(list(filter(lambda x: isinstance(x, feature), self.features))) > 0

    def get_feature(self, feature):
        return next(filter(lambda x: isinstance(x, feature), self.features), None)

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("builder", None)
        data.pop("config", None)
        data.pop("function_builder", None)

        if not data.stepFunctions.stateMachines:
            data.pop("stepFunctions", None)

        for plugin in data.plugins.all():
            plugin.pre_render(data)

        for feature in data.features:
            feature.pre_render(data)

        data.pop("features", None)
        data.pop("regions", None)

        return dumper.represent_dict(data)
