import itertools

from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict
from serverless.service.plugins.appsync import AppSync


import importlib


def import_variable(module_name: str, variable_name: str):
    module = importlib.import_module(module_name)
    if not hasattr(module, variable_name):
        return None

    return getattr(module, variable_name)


class AppSyncFunction(Function):
    yaml_tag = "!AppSyncFunction"

    def __init__(self, service, name, description, handler=None, timeout=None, layers=None, **kwargs):
        super().__init__(service, name, description, handler, timeout, layers, **kwargs)

        module_name, function_name = self.handler.rsplit(".", 1)
        graphql_app = import_variable(module_name, "app")

        if not graphql_app:
            return

        plugin = service.plugins.get(AppSync)

        plugin.dataSources[str(self.key.pascal)] = {
            "type": "AWS_LAMBDA",
            "config": {"functionName": str(self.key.pascal)},
        }

        for resolver in graphql_app._resolver_registry.resolvers.keys():
            plugin.resolvers[resolver] = {"kind": "UNIT", "dataSource": str(self.key.pascal)}

    @classmethod
    def to_yaml(cls, dumper, data):
        return super().to_yaml(dumper, data)
