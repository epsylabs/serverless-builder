from typing import Optional

import stringcase
from troposphere.dynamodb import (
    AttributeDefinition,
    KeySchema,
    TimeToLiveSpecification,
)
from troposphere.sqs import Queue

from serverless.aws.resources.dynamodb import Table
from serverless.aws.types import SQSArn
from serverless.service.environment import Environment
from serverless.service.plugins.python_requirements import PythonRequirements
from serverless.service.types import Identifier, YamlOrderedDict


class ScheduleEvent(YamlOrderedDict):
    yaml_tag = "schedule"

    def __init__(self, expression):
        super().__init__()
        self.expression = expression


class Function(YamlOrderedDict):
    yaml_tag = "!Function"

    def __init__(
            self,
            service,
            name,
            description,
            handler=None,
            timeout=None,
            layers=None,
            force_name=None,
            idempotency=None,
            **kwargs,
    ):
        super().__init__()
        self._service = service

        self.key = stringcase.pascalcase(stringcase.snakecase(name).lower())
        self.name = (
            force_name
            if force_name
            else Identifier(
                self._service.service.spinal.lower() + "-${sls:stage}" + "-" + stringcase.spinalcase(name).lower()
            )
        )
        self.description = description

        if not handler:
            handler = f"{self._service.service.snake}.{stringcase.snakecase(name)}.handler"

        self.handler = handler
        self.events = []

        configured = list(filter(lambda x: x.get("Ref") == "PythonRequirementsLambdaLayer", layers or []))
        if self._service.plugins.get(PythonRequirements) and not configured:
            if not layers:
                layers = []

            layers.append({"Ref": "PythonRequirementsLambdaLayer"})

        if layers:
            self.layers = layers

        if timeout:
            self.timeout = timeout

        if idempotency:
            self.with_idempotency(idempotency)

        for name, value in kwargs.items():
            setattr(self, name, value)

    def get_attr(self, attr):
        return {"Fn::GetAtt": [self.resource_name(), attr]}

    def arn(self):
        return self.get_attr("Arn")

    def resource_name(self):
        return f"{self.key}LambdaFunction"

    def trigger(self, event):
        self.events.append(event)

        return event

    def apply(self, **kwargs):
        for event in self.events:
            for k, v in kwargs.items():
                event[k] = v

    def use_async_dlq(self, onErrorDLQArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> None:
        """
        @param onErrorDLQArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """
        if not onErrorDLQArn:
            name = f"{self.name.spinal}-dlq"
            queue = Queue(
                QueueName=f"{self.name.spinal}-dlq",
                title=f"{self.name.pascal}DLQ",
                MessageRetentionPeriod=MessageRetentionPeriod,
            )
            self._service.resources.add(queue)

            onErrorDLQArn = SQSArn(name)
            self._service.provider.iam.allow(
                sid=f"{queue.title}Writer",
                permissions=["sqs:GetQueueUrl", "sqs:SendMessageBatch", "sqs:SendMessage"],
                resources=[str(onErrorDLQArn)],
            )
        self.onError = {"Fn::Sub": onErrorDLQArn}

        return self

    def use_destination_dlq(self, onFailuredlqArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> None:
        """
        @param onFailuredlqArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """
        if not onFailuredlqArn:
            name = f"{self.name.spinal}-dlq"
            queue = Queue(
                QueueName=f"{self.name.spinal}-dlq",
                title=f"{self.name.pascal}DLQ",
                MessageRetentionPeriod=MessageRetentionPeriod,
            )
            self._service.resources.add(queue)
            onFailuredlqArn = SQSArn(name)

        self.destinations = dict(onFailure=onFailuredlqArn)

        return self

    def with_vpc(self, security_group_names=None, subnet_names=None):
        if security_group_names:
            self.vpcDiscovery = dict(securityGroups=[dict(tagKey="Name", tagValues=security_group_names.copy())])

        return self

    def with_idempotency(self, table_name=None):
        table_name = table_name or f"{self.name.pascal}Idempotency"

        idempotency_table = Table(
            TableName=table_name,
            # DeletionPolicy=Retain,  # temp
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                AttributeDefinition(AttributeName="id", AttributeType="S"),
            ],
            KeySchema=[
                KeySchema(AttributeName="id", KeyType="HASH"),
            ],
            TimeToLiveSpecification=TimeToLiveSpecification(AttributeName="expiration", Enabled=True),
        )
        idempotency_table.with_full_access()
        self._service.resources.add(idempotency_table)
        env = self.get("environment", Environment())
        env.envs["IDEMPOTENCY_TABLE"] = idempotency_table.table_arn
        self.environment = env

        return self

    @classmethod
    def to_yaml(cls, dumper, data):
        events = data.events
        data.pop("_service", None)
        data.pop("key", None)

        if not data.events:
            del data["events"]
        else:
            data.events = [{event.yaml_tag: event} for event in events]

        return dumper.represent_dict(data)
