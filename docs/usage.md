# Usage

## Simplest possible example
```python 
from serverless import Service
from serverless.provider import AWSProvider

service = Service(
    "service-name",
    "Description of my service",
    AWSProvider()
)

service.render()
```

## Lambda functions
`serverless-builder` allows you easily define different types of lambdas. In many cases it also takes care, by default, for setting up Dead Letter Queue (DLQ) or its asynchronous equivalent, Retry Policy or idempotency.

`serverless-builder` will take care of creating any required resources as well as IAM permissions. 

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

## EventBridge
```python
service.builder.function.event_bridge(
    "event_bridge_function",
    "sample event bridge function",
    "epsy",
    {"source": ["saas.external"]},
)
```
