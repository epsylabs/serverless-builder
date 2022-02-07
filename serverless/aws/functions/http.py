import itertools

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

    def __init__(self, path, method, authorizer=None, request_parameters_querystrings=None):
        super().__init__()
        self.path = path
        self.method = method

        if authorizer:
            self.authorizer = authorizer

        if request_parameters_querystrings:
            self.request = {"parameters": {"querystrings": request_parameters_querystrings}}


class HTTPFunction(Function):
    yaml_tag = "!HTTPFunction"

    POST = "POST"
    GET = "GET"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    ANY = "ANY"

    def __init__(
        self,
        service,
        name,
        description,
        path,
        method,
        authorizer=None,
        handler=None,
        timeout=None,
        layers=None,
        request_parameters_querystrings=None,
        **kwargs
    ):
        super().__init__(service, name, description, handler, timeout, layers, **kwargs)

        if isinstance(path, str):
            path = [path]
        if isinstance(method, str):
            method = [method]

        # Set up an HTTP event on all combinations of path and method
        for p, m in itertools.product(path, method):
            self.trigger(HTTPEvent(p, m, authorizer, request_parameters_querystrings))
