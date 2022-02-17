<h2 align="center">serverless-builder</h2>
<p align="center">
<a href="https://pypi.org/project/serverless-builder/"><img alt="PyPI" src="https://img.shields.io/pypi/v/serverless-builder"></a>
<a href="https://pypi.org/project/serverless-builder/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/serverless-builder.svg"></a>
<a href="https://github.com/epsylabs/serverless-builder/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/lucyna.svg"></a>
</p>

Python interface to easily generate [serverless.yml](https://www.serverless.com/) file.

Massive thanks goes to [@dxd1](https://github.com/dxd1) for his original idea and implementation.

## Why
`serverless.yml` easily can become a massive file with hundreds of lines, even if you have only a couple of services.

Modifying even semi advanced project can be difficult. Adding plugins and configuration for it, making sure your endless resources are configured correctly, making sure that you follow best practices.
If you will multiple that by all microservices you have, it can be really painful.

## How
`serverless-builder` comes and tries to help you with those tasks.
- plugin management (with autoconfiguration)
- function factory (with some best practice hints (DLQ))
- autoconfiguration of some provider specific features like AWS X-Ray
- monitoring support (wip)
- easy resource manipulation with troposphere lib https://github.com/cloudtools/troposphere (but if you want you can use old good dict)
- easier IAM management with predefined permission sets
- built-in support for any serverless attributes

# Example

```python
from serverless.aws.functions.event_bridge import RetryPolicy
from serverless.aws.functions.http import HTTPFunction
from serverless import Service
from serverless.provider import AWSProvider
from serverless.aws.features import XRay
from serverless.aws.iam.dynamodb import DynamoDBReader
from serverless.plugins import ComposedVars, PythonRequirements, Prune

from troposphere.dynamodb import Table, AttributeDefinition, KeySchema

service = Service(
    "service-name",
    "some dummy service",
    AWSProvider()
)
service.plugins.add(ComposedVars())
service.plugins.add(Prune())
service.plugins.add(PythonRequirements())

table = Table(
    "TestTable",
    BillingMode="PAY_PER_REQUEST",
    AttributeDefinitions=[
        AttributeDefinition(AttributeName="name", AttributeType="S")
    ],
    KeySchema=[KeySchema(AttributeName="name", KeyType="HASH")]
)

service.enable(XRay())
service.provider.iam.apply(DynamoDBReader(table))

service.builder.function.generic("test", "description")
service.builder.function.http("test", "description", "/", HTTPFunction.POST)

# Multiple events with different paths and/or methods can be set up for the same handler
# This will add the same handler to all of these: POST /, POST /alias, PUT /, PUT /alias
service.builder.function.http("test", "description", ["/", "/alias"], ["POST", "PUT"], handler="shared.handler")

# Context with pre-defined setup
with service.preset(
    layers=[{"Ref": "PythonRequirementsLambdaLayer"}],
    handler="test.handlers.custom_handler.handle"
) as p:
    p.http_get("test-list", "List all tests", "/")
    p.http_get("test-get", "Get one test", "/{test_id}")

event_bridge_function = service.builder.function.event_bridge(
    "event_bridge_function",
    "sample event bridge function",
    "epsy",
    {"source": ["saas.external"]},
)

event_bridge_function.use_delivery_dlq(RetryPolicy(5, 300))
event_bridge_function.use_async_dlq()

service.resources.add(table)

service.render()
```
