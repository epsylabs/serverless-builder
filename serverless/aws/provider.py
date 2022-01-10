import yaml

from serverless.aws.functions.event_bridge import EventBridgeFunction
from serverless.aws.functions.generic import Function
from serverless.aws.functions.http import HTTPFunction
from serverless.aws.iam import IAMManager
from serverless.service.environment import Environment
from serverless.service.types import Provider as BaseProvider


class Runtime(yaml.YAMLObject):
    NODE_10 = "nodejs10"
    NODE_12 = "nodejs12"
    NODE_14 = "nodejs14"

    PYTHON_2_7 = "python2.7"
    PYTHON_3_6 = "python3.6"
    PYTHON_3_7 = "python3.7"
    PYTHON_3_8 = "python3.8"
    PYTHON_3_9 = "python3.9"

    yaml_tag = "!Runtime"

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_str(data)


class FunctionBuilder:
    def __init__(self, service):
        super().__init__()
        self.service = service

    def generic(self, name, description, handler=None, timeout=None, layers=None) -> Function:
        fn = Function(self.service, name, description, handler, timeout, layers)
        self.service.functions.add(fn)

        return fn

    def http(
            self, name, description, path, method, authorizer=None, handler=None, timeout=None, layers=None
    ) -> HTTPFunction:
        fn = HTTPFunction(self.service, name, description, path, method, authorizer, handler, timeout, layers)
        self.service.functions.add(fn)

        return fn

    def event_bridge(
            self,
            name,
            description,
            eventBus,
            pattern=None,
            deadLetterQueueArn=None,
            retryPolicy=None,
            handler=None,
            timeout=None,
            layers=None,
    ) -> EventBridgeFunction:
        fn = EventBridgeFunction(
            self.service,
            name,
            description,
            eventBus,
            pattern,
            deadLetterQueueArn,
            retryPolicy,
            handler,
            timeout,
            layers,
        )
        self.service.functions.add(fn)

        return fn


class Provider(BaseProvider, yaml.YAMLObject):
    yaml_tag = "!Provider"

    def __init__(
            self, runtime=Runtime.PYTHON_3_8, extra_tags=None, timeout=60, stage="development", environment=None, /,
            **kwds
    ):
        super().__init__(**kwds)

        self.deploymentBucket = None
        self._service = None
        self.function_builder = None

        self.name = "aws"
        self.runtime = runtime
        self.stackName = "${self:service}"
        self.timeout = timeout
        self.stage = stage
        self.tags = extra_tags or {}
        self.lambdaHashingVersion = 20201221
        self.environment = environment or Environment()
        self.iam = None
        self.apiGateway = dict(
            shouldStartNameWithService=True
        )
        self.eventBridge = dict(
            useCloudFormation=True
        )

    def configure(self, service):
        self._service = service
        self.deploymentBucket = dict(
            name=f"sls-deployments.${{self:custom.region}}."
                 f"${{self:custom.stage}}{self._service.config.domain(prefix='.')}"
        )
        self.tags["SERVICE"] = self._service.service.spinal
        self.iam = IAMManager(self._service)
        self.function_builder = FunctionBuilder(self._service)

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("_service", None)
        data.pop("function_builder", None)

        return dumper.represent_dict(data)
