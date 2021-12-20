from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class HTTPAuthorizer(YamlOrderedDict):
    yaml_tag = "!Authorizer"

    def __init__(self, name, identitySource, type):
        super().__init__()
        self.identitySource = identitySource
        self.name = name
        self.type = type


class HTTPEvent(YamlOrderedDict):
    yaml_tag = "http"

    def __init__(self, path, method, authorizer=None):
        super().__init__()
        self.path = path
        self.method = method

        if authorizer:
            self.authorizer = authorizer


class HTTPFunction(Function):
    yaml_tag = "!HTTPFunction"

    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"

    def __init__(
        self, service, name, description, path, method, authorizer=None, handler=None, timeout=None, layers=None
    ):
        super().__init__(service, name, description, handler, timeout, layers)
        self.trigger(HTTPEvent(path, method, authorizer))
