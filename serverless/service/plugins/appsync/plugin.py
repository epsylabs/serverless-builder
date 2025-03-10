from typing import List, Union

from serverless.service.plugins.generic import Generic
from serverless.service.types import YamlOrderedDict


class IAMAuthentication(YamlOrderedDict):
    yaml_tag = "!IAMAuthentication"

    def __init__(self):
        super().__init__()
        self.type = "AWS_IAM"


class CognitoAuthentication(YamlOrderedDict):
    yaml_tag = "!CognitoAuthentication"

    def __init__(self, user_pool):
        super().__init__()
        self.type = "AMAZON_COGNITO_USER_POOLS"
        self.config = {"userPoolId": user_pool}


class ResolverExtra(object):
    def __init__(self, resolver, prefix=False, max_batch_size=None, request=None, response=None):
        super().__init__()
        self.resolver = resolver
        self.prefix = prefix
        self.max_batch_size = max_batch_size
        self.request = request
        self.response = response


class AppSync(Generic):
    """
    Plugin: https://github.com/sid88in/serverless-appsync-plugin
    """

    yaml_tag = "!AppSyncPlugin"

    def __init__(
        self,
        schema="schema.graphql",
        authentication=None,
        xray=False,
        resolvers=None,
        data_sources=None,
        additional_authentications=None,
        namespace=None,
        namespace_excluded=None,
        include_top_namespace_resolver=True,
        resolver_extras: Union[List[ResolverExtra], None] = None,
        **kwargs
    ):
        super().__init__("serverless-appsync-plugin")
        self.schema = schema
        self.authentication = authentication or IAMAuthentication()
        self.additionalAuthentications = additional_authentications or []
        self.xrayEnabled = xray
        self.dataSources = data_sources or {}
        self.resolvers = resolvers or {}
        self.namespace = namespace
        self.resolver_extras = resolver_extras or []
        self.update(kwargs)
        self.topNamespaceResolver = include_top_namespace_resolver

    def enable(self, service):
        export = dict(self)
        export["name"] = str(service.service)
        export.pop("namespace")
        export.pop("resolver_extras")
        export.pop("topNamespaceResolver")

        service.appSync = export
