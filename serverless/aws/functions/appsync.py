import itertools

from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict, Identifier
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
        prefix = plugin.namespace if plugin.namespace else ""

        plugin.dataSources[str(self.key.pascal)] = {
            "type": "AWS_LAMBDA",
            "config": {"functionName": str(self.key.pascal)},
        }

        extras_map = {extra.resolver.lower(): extra for extra in plugin.resolver_extras}

        for name, resolver in graphql_app._resolver_registry.resolvers.items():
            gql_type, gql_field = name.split(".")

            extras = extras_map.get(name.lower())

            if not extras or extras.prefix:
                gql_type = Identifier(prefix + str(gql_type)).camel

            defintion = {"type": gql_type, "field": gql_field, "kind": "UNIT", "dataSource": str(self.key.pascal)}

            if extras:
                defintion.update({"maxBatchSize": extras.max_batch_size})

            plugin.resolvers[str(Identifier(gql_type).camel) + str(Identifier(gql_field).camel)] = defintion

    @classmethod
    def to_yaml(cls, dumper, data):
        return super().to_yaml(dumper, data)
