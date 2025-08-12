from troposphere.awslambda import Version, Alias as TAlias

from serverless.aws.resources import Resource


class Alias(Resource):
    def __init__(self, function, alias, **kwargs):
        self.function = function
        self.alias = alias

    def resources(self):
        version = Version(title=f"{self.function.key.resource}Version", FunctionName=str(self.function.name), Description="${sls:instanceId}")
        alias = TAlias(title=f"{self.function.key.resource}Alias", Name=self.alias, FunctionName=str(self.function.name), FunctionVersion=version.get_att("Version"))
        return [
            version,
            alias
        ]
