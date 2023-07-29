# Functions

`serverless-builder` has a built-in support for common lambda functions with best practices applied by default.



## HTTP
There are two ways of generating HTTP endpoint. You can use one of the helper functions e.g. `http_get`, `http_post`,
or just more generic `http` with passed explicitly HTTP method.

```python
from serverless.aws.functions.http import HTTPFunction

service.builder.function.http_get("test-list", "List all tests", "/")
service.builder.function.http_post("test-list", "List all tests", "/")
service.builder.function.http_put("test-list", "List all tests", "/")
service.builder.function.http_patch("test-list", "List all tests", "/")
service.builder.function.http_delete("test-list", "List all tests", "/")
service.builder.function.http_options("test-list", "List all tests", "/")
service.builder.function.http_any("test-list", "List all tests", "/")
service.builder.function.http("test", "description", "/", HTTPFunction.POST)
```

Call to any of the above functions will generate serverless.com funciton with its corresponding HTTP event e.g.:
```yaml
functions:
  Test:
    name: service-name-${sls:stage}-test
    description: description
    handler: service_name.test.handler
    events:
    - http:
        path: /
        method: POST
```

### EventBridge
```python
service.builder.function.event_bridge(
    "event_bridge_function",
    "sample event bridge function",
    "epsy",
    {"source": ["saas.external"]},
)
```

#### With DLQ
By default `function.event_bridge` will setup DLQ for your lambda that processes EventBridge messages.

### S3
```python
service.builder.function.s3(
        "Reload",
        "Reloads list of IDs",
        timeout=30,
        bucket="${self:service}.${ssm:/global/primary-domain}",
        event="s3:ObjectCreated:*",
        rules=[{"prefix": "list/ids"}],
    )
```

### Websockets
```python
from serverless.aws.functions.websocket import WebsocketEvent, Authorizer as WebsocketEventAuthorizer


service.builder.function.websocket(
    "handler_connect",
    "Handles client opening Websocket connection",
    events=[WebsocketEvent(route="$connect", authorizer=WebsocketEventAuthorizer("HandleAuthorization"))],
    handler="my_module.handler.handle_connect",
)
```
