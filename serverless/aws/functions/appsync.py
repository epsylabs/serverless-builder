import importlib
from pathlib import Path

from serverless.aws.functions.generic import Function
from serverless.service.plugins.appsync import AppSync
from serverless.service.plugins.appsync.plugin import ResolverExtra
from serverless.service.types import Identifier


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

        datasource_config = {
            'functionName': str(self.key.pascal)
        }

        if "provisionedConcurrency" in kwargs or "concurrencyAutoscaling" in kwargs:
            if isinstance(kwargs.get("concurrencyAutoscaling"), dict):
                fn_alias = kwargs.get("concurrencyAutoscaling", {}).get("alias", "provisioned")
            else:
                fn_alias = "provisioned"

            service.custom["ds" + str(self.key.pascal)] = {
                0: {
                    'functionName': str(self.key.pascal)
                },
                'default': {
                    'functionName': str(self.key.pascal),
                    'functionAlias': fn_alias
                }
            }

            datasource_config = '${self:custom.ds' + str(self.key.pascal) + '.${self:custom.vars.provisioning.provisionedConcurrency}, self:custom.ds'+ str(self.key.pascal) +'.default}'


        plugin.dataSources[str(self.key.pascal)] = {
            "type": "AWS_LAMBDA",
            "config": datasource_config
        }

        extras_map = {extra.resolver.lower(): extra for extra in plugin.resolver_extras}

        has_query = False
        has_mutation = False

        import __main__ as main

        batch_resolver = Path(main.__file__).parent.absolute().joinpath("batch.response.vtl")
        with open(batch_resolver, "w+") as f:
            f.write("$util.toJson($context.result)")

        mutation_resolver = Path(main.__file__).parent.absolute().joinpath("mutation.response.vtl")
        with open(mutation_resolver, "w+") as f:
            f.write("""
#if (!$util.isNull($ctx.error))
  $util.error(
    $util.defaultIfNull($ctx.error.message, "UnhandledError"),
    $util.defaultIfNull($ctx.error.type, "Lambda:Unhandled"),
    $util.defaultIfNull($ctx.error.data, {}),
    $util.defaultIfNull($ctx.error.errorInfo, {})
  )
#end

#if (!$util.isNull($ctx.result) && !$util.isNull($ctx.result.error))
  $util.error(
    $util.defaultIfNull($ctx.result.error.message, "UnknownError"),
    $util.defaultIfNull($ctx.result.error.type, "BadRequest"),
    $util.defaultIfNull($ctx.result.error.data, {}),
    $util.defaultIfNull($ctx.result.error.info, {})
  )
#end

$util.toJson($ctx.result)
""".strip())

        for name, resolver in {
            **graphql_app._resolver_registry.resolvers,
            **graphql_app._batch_resolver_registry.resolvers,
        }.items():
            gql_type, gql_field = name.split(".")
            if gql_type.lower().endswith("query"):
                has_query = True

            if gql_type.lower().endswith("mutation"):
                has_mutation = True

            extras = extras_map.get(name.lower(), ResolverExtra(name))

            defintion = {"type": gql_type, "field": gql_field, "kind": "UNIT", "dataSource": str(self.key.pascal)}

            if name in graphql_app._batch_resolver_registry.resolvers:
                extras.max_batch_size = extras.max_batch_size or 10
                extras.response = extras.response or Path(batch_resolver).name

            if gql_type.lower().endswith("mutation"):
                extras.response = extras.response or Path(mutation_resolver).name

            if extras.max_batch_size:
                defintion["maxBatchSize"] = extras.max_batch_size

            if extras.response:
                defintion["response"] = extras.response

            if extras.request:
                defintion["request"] = extras.request

            plugin.resolvers[str(Identifier(gql_type).camel) + str(Identifier(gql_field).camel)] = defintion

        if plugin.namespace:
            parts = plugin.namespace.split(".")

            if has_query:
                if len(parts) == 1 or plugin.topNamespaceResolver:
                    plugin.resolvers["Query"] = {
                        "type": "Query",
                        "field": Identifier(parts[0]).camel.lower(),
                        "functions": [],
                    }
                if len(parts) > 1:
                    plugin.resolvers[Identifier(parts[0] + "Query").camel] = {
                        "type": Identifier(parts[0] + "Query").camel,
                        "field": Identifier(parts[1]).camel.lower(),
                        "functions": [],
                    }

            if has_mutation:
                if len(parts) == 1 or plugin.topNamespaceResolver:
                    plugin.resolvers["Mutation"] = {
                        "type": "Mutation",
                        "field": Identifier(parts[0]).camel.lower(),
                        "functions": [],
                    }

                if len(parts) > 1:
                    plugin.resolvers[Identifier(parts[0] + "Mutation").camel] = {
                        "type": Identifier(parts[0] + "Mutation").camel,
                        "field": Identifier(parts[1]).camel.lower(),
                        "functions": [],
                    }

    @classmethod
    def to_yaml(cls, dumper, data):
        return super().to_yaml(dumper, data)
