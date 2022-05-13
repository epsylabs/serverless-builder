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

### HTTP
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

## Predefined settings

### Within your service definition
Quite often multiple resources share same set of parameters, good example are layers or auth method shared across multiple functions.

For that purpose we have `preset` function.

```python
with service.preset(
    layers=[{"Ref": "PythonRequirementsLambdaLayer"}],
    handler="test.handlers.custom_handler.handle"
) as p:
    p.http_get("test-list", "List all tests", "/")
    p.http_get("test-get", "Get one test", "/{test_id}")
```

In this case both functions will also have two extra parameters set, `layers` and `handler`

### Across multiple repositories
With your team you can agree on list of plugins, integrations and settings that should be used across multiple repositories (micro services).

The easiest way to share those settings is to override default `Service` class and extract it to separated repository. 

```python
from serverless import Configuration
from serverless import Service as BaseService
from serverless.aws.features import XRay
from serverless.aws.features.encryption import Encryption
from serverless.aws.provider import Provider as AWSProvider
from serverless.integration.powertools import Powertools
from serverless.integration.sentry import Sentry
from serverless.service.environment import Environment
from serverless.service.plugins.prune import Prune
from serverless.service.plugins.python_requirements import PythonRequirements


class Service(BaseService):
    yaml_tag = "!Service"

    def __init__(self, name: str, description: str, environment=None, sentry_dsn=None, **kwds):
        defaults = dict(
            LOG_LEVEL="${self:custom.vars.log_level}",
            SERVICE="${self:service}",
            STAGE="${sls:stage}",
        )

        defaults.update(environment.envs)
        env = Environment(**defaults)

        super().__init__(
            name, description, AWSProvider(environment=env), config=Configuration(domain="epsy.app"), **kwds
        )
        
        self.plugins.add(Prune())
        self.plugins.add(PythonRequirements(layer=False))

        if sentry_dsn:
            self.enable(Sentry(sentry_dsn=sentry_dsn))

        self.enable(XRay())
        self.enable(Powertools())
        self.enable(Encryption())
```

In your project then you can use your custom `Service` class.
