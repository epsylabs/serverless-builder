from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class Authorizer(YamlOrderedDict):
    yaml_tag = "Authorizer"

    def __init__(self, name: str, identity_source: list = None):
        super().__init__()
        self.name = name

        if identity_source is not None:
            self.identitySource = identity_source


class WebsocketEvent(YamlOrderedDict):
    yaml_tag = "websocket"

    def __init__(self, route: str, routeResponseSelectionExpression: str = None, authorizer: Authorizer = None):
        super().__init__()
        self.route = route

        if routeResponseSelectionExpression:
            self.routeResponseSelectionExpression = routeResponseSelectionExpression

        if authorizer:
            self.authorizer = authorizer


class WebsocketFunction(Function):
    yaml_tag = "!WebsocketFunction"

    def __init__(
        self,
        service,
        name,
        description,
        route="$default",
        routeResponseSelectionExpression=None,
        authorizer=None,
        handler=None,
        timeout=None,
        layers=None,
        use_dlq=True,
        use_async_dlq=True,
        **kwargs,
    ):
        super().__init__(
            service, name, description, handler, timeout, layers, use_dlq=use_dlq, use_async_dlq=use_async_dlq, **kwargs
        )
        self.trigger(WebsocketEvent(route, routeResponseSelectionExpression, authorizer))
