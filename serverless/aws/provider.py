import yaml

from serverless.aws.functions.dynamodb import DynamoDBStreamFunction
from serverless.aws.functions.event_bridge import EventBridgeFunction
from serverless.aws.functions.generic import Function
from serverless.aws.functions.http import HTTPFunction
from serverless.aws.functions.kinesis import KinesisFunction
from serverless.aws.functions.s3 import S3Function
from serverless.aws.functions.sqs import SQSFunction
from serverless.aws.iam import ServicePolicyBuilder
from serverless.service.environment import Environment
from serverless.service.types import Provider as BaseProvider


class Runtime(yaml.YAMLObject):
    NODE_10 = "nodejs10"
    NODE_12 = "nodejs12"
    NODE_14 = "nodejs14"
    NODE_16 = "nodejs16"

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

    def generic(self, name, description, handler=None, timeout=None, layers=None, **kwargs) -> Function:
        fn = Function(self.service, name, description, handler, timeout, layers, **kwargs)
        self.service.functions.add(fn)

        return fn

    def http(
        self, name, description, path, method, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(self.service, name, description, path, method, authorizer, handler, timeout, layers, **kwargs)
        self.service.functions.add(fn)

        return fn

    def http_post(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.POST, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_get(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.GET, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_put(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.PUT, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_patch(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.PATCH, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_delete(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.DELETE, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_options(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.OPTIONS, authorizer, handler, timeout, layers, **kwargs
        )
        self.service.functions.add(fn)

        return fn

    def http_any(
        self, name, description, path, authorizer=None, handler=None, timeout=None, layers=None, **kwargs
    ) -> HTTPFunction:
        fn = HTTPFunction(
            self.service, name, description, path, HTTPFunction.ANY, authorizer, handler, timeout, layers, **kwargs
        )
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
        **kwargs,
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
            **kwargs,
        )
        self.service.functions.add(fn)

        return fn

    def s3(self, name, description, bucket, event, rules=None, existing=None, handler=None, timeout=None, layers=None, **kwargs):
        fn = S3Function(self.service, name, description, bucket, event, rules, existing, handler, timeout, layers, **kwargs)
        self.service.functions.add(fn)

        return fn

    def kinesis(self, stream, name, description, **kwargs):
        fn = KinesisFunction(stream, self.service, name, description, **kwargs)
        self.service.functions.add(fn)

        return fn

    def dynamodb_stream(self, stream, name, description, **kwargs):
        fn = DynamoDBStreamFunction(stream, self.service, name, description, **kwargs)
        self.service.functions.add(fn)

        return fn

    def sqs(self, name, description, arn, **kwargs):
        fn = SQSFunction(self.service, name, description, arn, **kwargs)
        self.service.functions.add(fn)

        return fn


class Provider(BaseProvider, yaml.YAMLObject):
    yaml_tag = "!Provider"

    def __init__(
        self, runtime=Runtime.PYTHON_3_8, extra_tags=None, timeout=10, stage="${sls:stage}", environment=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.deploymentBucket = None
        self._service = None
        self.function_builder = None

        self.name = "aws"
        self.runtime = runtime
        self.stackName = "${self:service}-${sls:stage}"
        self.timeout = timeout
        self.stage = stage
        self.tags = extra_tags or {}
        self.stackTags = {}
        self.lambdaHashingVersion = 20201221
        self.environment = environment or Environment()
        self.iam = None
        self.apiGateway = dict(shouldStartNameWithService=True)
        self.eventBridge = dict(useCloudFormation=True)

    def configure(self, service):
        self._service = service

        if service.config.domain:
            self.deploymentBucket = dict(name=f"sls-deployments.${{aws:region}}.${{sls:stage}}.{service.config.domain}")

        self.tags["SERVICE"] = "${self:service}"
        self.tags["REGION"] = "${aws:region}"
        self.tags["STAGE"] = "${sls:stage}"
        self.stackTags = self.tags.copy()
        self.iam = ServicePolicyBuilder(self._service)
        self.function_builder = FunctionBuilder(self._service)

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("_service", None)
        data.pop("function_builder", None)
        if not data.get("deploymentBucket"):
            data.pop("deploymentBucket", None)

        return dumper.represent_dict(data)
