from serverless.service.plugins.generic import Generic
from serverless.service.types import YamlOrderedDict


class IAMAuthentication(YamlOrderedDict):
    yaml_tag = "!IAMAuthentication"

    def __init__(self):
        super().__init__()
        self.type = "AWS_IAM"


class AppSync(Generic):
    """
    Plugin: https://github.com/sid88in/serverless-appsync-plugin
    """

    yaml_tag = "!AppSyncPlugin"

    def __init__(
        self, schema="schema.graphql", authentication=None, xray=False, resolvers=None, data_sources=None, **kwargs
    ):
        super().__init__("serverless-appsync-plugin")
        self.schema = schema
        self.authentication = authentication or IAMAuthentication()
        self.xrayEnabled = xray
        self.dataSources = data_sources or {}
        self.resolvers = resolvers or {}
        self.update(kwargs)

    def enable(self, service):
        export = dict(self)
        export["name"] = str(service.service)

        service.appSync = export
