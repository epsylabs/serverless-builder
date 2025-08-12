from troposphere.awslambda import Version, Alias as TAlias

from serverless.aws.resources import Resource
from serverless.service.resources import Condition


class Alias(Resource):
    def __init__(self, function, alias, condition: Condition, **kwargs):
        self.function = function
        self.alias = alias
        self.condition = condition

    def resources(self):
        version_kwargs = dict(
            title=f"{self.function.key.resource}Version",
            FunctionName=str(self.function.name),
            Description="${sls:instanceId}",
        )

        if self.condition:
            version_kwargs["Condition"] = self.condition.title

        version = Version(**version_kwargs)

        alias_kwargs = dict(
            title=f"{self.function.key.resource}Alias",
            Name=self.alias,
            FunctionName=str(self.function.name),
            FunctionVersion=version.get_att("Version"),
        )

        if self.condition:
            alias_kwargs["Condition"] = self.condition.title

        return [version, TAlias(**alias_kwargs)]
