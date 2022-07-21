# Advanced 

## Multi Region deployments

## Default values (scope management)

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


## Presets

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
