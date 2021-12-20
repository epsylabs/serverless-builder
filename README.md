# serverless-builder

Python interface to easily generate `serverless.yml`.

Massive thanks goes to @dxd1 for his original idea and implementation.


## Why

serverless.yml easily can become a massive file with hundreds of lines even if you have only a couple of services.
Adding plugins, features, naming patterns etc. become more and more complicated and each change can be really painful
due to multiple sections of the file which are affected.

## How

serverless-builder is an object oriented builder of the `serverless.yml` file with build in support for:

- plugins management (with autoconfiguration)
- function factory (with some best practice hints (DLQ)
- autoconfiguration of some provider specific features like AWS X-Ray
- monitoring support (wip)
- easy resource manipulation with troposphere lib https://github.com/cloudtools/troposphere
- easier IAM management with predefine permission sets
- build-in support for any serverless attributes


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

service.provider.functions.generic("test", "description")
service.provider.functions.http("test", "description", "/", HTTPFunction.POST)

event_bridge_function = service.provider.functions.event_bridge(
    "event_bridge_function",
    "sample event bridge function",
    "epsy",
    {"source": ["saas.external"]},
)

event_bridge_function.use_delivery_dql(RetryPolicy(5, 300))
event_bridge_function.use_async_dlq()

service.resources.add(table)

service.render()
```
