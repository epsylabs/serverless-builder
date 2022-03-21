from typing import Optional

import stringcase
from troposphere.dynamodb import (
    AttributeDefinition,
    KeySchema,
    TimeToLiveSpecification,
)
from serverless.aws.iam import PolicyBuilder, FunctionPolicyBuilder
from serverless.aws.iam.dynamodb import DynamoDBFullAccess
from serverless.aws.iam.sqs import SQSPublisher
from serverless.aws.resources.dynamodb import Table
from serverless.aws.resources.sqs import Queue
from serverless.aws.types import SQSArn
from serverless.service.environment import Environment
from serverless.service.plugins.iam_roles import IAMRoles
from serverless.service.plugins.lambda_dlq import LambdaDLQ
from serverless.service.plugins.python_requirements import PythonRequirements
from serverless.service.types import Identifier, YamlOrderedDict
from troposphere.cloudwatch import Alarm, MetricDimension


class ScheduleEvent(YamlOrderedDict):
    yaml_tag = "schedule"

    def __init__(self, expression):
        super().__init__()
        self.rate = expression


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

        if self._service.plugins.get(IAMRoles):
            self.iamRoleStatements = FunctionPolicyBuilder(self.name, self._service)
            self.iamRoleStatementsName = self.iamRoleStatements.role
            self.iamRoleStatementsInherit = True

        configured = list(filter(lambda x: x.get("Ref") == "PythonRequirementsLambdaLayer", layers or []))
        if (
            self._service.plugins.get(PythonRequirements)
            and self._service.plugins.get(PythonRequirements).layer
            and not configured
        ):
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

    @property
    def iam(self):
        if not self._service.plugins.get(IAMRoles):
            self._service.plugins.add(IAMRoles())

        if not self.iamRoleStatements:
            self.iamRoleStatements = FunctionPolicyBuilder(self.name, self._service)
            self.iamRoleStatementsName = self.iamRoleStatements.role
            self.iamRoleStatementsInherit = True

        return self.iamRoleStatements

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

    def use_dlq(self, onErrorDLQArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> None:
        """
        @param onErrorDLQArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """

        if not self._service.plugins.has(LambdaDLQ):
            self._service.plugins.add(LambdaDLQ())

        if not onErrorDLQArn:
            onErrorDLQArn = self._ensure_dlq(MessageRetentionPeriod)

            self.iam.allow(
                sid=f"{self.name.pascal}DLQWriter",
                permissions=["sqs:GetQueueUrl", "sqs:SendMessageBatch", "sqs:SendMessage"],
                resources=[onErrorDLQArn.get("arn")],
            )

        self.deadLetter = dict(targetArn=self._ensure_dlq(MessageRetentionPeriod).get("arn"))

        return self

    def use_async_dlq(self, onFailuredlqArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> None:
        """
        @param onFailuredlqArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """
        if not onFailuredlqArn:
            onFailuredlqArn = self._ensure_dlq(MessageRetentionPeriod).get("arn")

        self.iam.apply(SQSPublisher(onFailuredlqArn))

        self.destinations = dict(onFailure=onFailuredlqArn)

        return self

    def _ensure_dlq(self, MessageRetentionPeriod):
        name = f"{self.name.spinal}-dlq"
        queue = Queue(
            QueueName=name,
            title=f"{self.name.pascal}DLQ",
            MessageRetentionPeriod=MessageRetentionPeriod,
        )
        self._service.resources.add(queue)

        self._service.resources.add(
            Alarm(
                f"{self.name.pascal}DLQAlarm",
                AlarmDescription=f"Lambda: {self.name} rejected event in DLQ",
                AlarmActions=["arn:aws:sns:${aws:region}:${aws:accountId}:foxglove-${sls:stage}-cloudwatch-alerts"],
                Namespace="AWS/SQS",
                MetricName="ApproximateNumberOfMessagesVisible",
                Dimensions=[MetricDimension(Name="QueueName", Value=name)],
                Statistic="Sum",
                Period=60,
                EvaluationPeriods=1,
                Threshold=1,
                ComparisonOperator="GreaterThanOrEqualToThreshold",
            )
        )

        return {"Ref": f"{self.name.pascal}DLQ", "arn": SQSArn(name)}

    def with_vpc(self, security_group_names=None, subnet_names=None):
        if security_group_names:
            self.vpcDiscovery = dict(securityGroups=[dict(tagKey="Name", tagValues=security_group_names.copy())])

        return self

    def with_idempotency(self, table_name=None):
        table_name = table_name or f"{self.name.pascal}Idempotency"

        idempotency_table = Table(
            TableName=table_name,
            DeletionPolicy="Retain",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                AttributeDefinition(AttributeName="id", AttributeType="S"),
            ],
            KeySchema=[
                KeySchema(AttributeName="id", KeyType="HASH"),
            ],
            TimeToLiveSpecification=TimeToLiveSpecification(AttributeName="expiration", Enabled=True),
        )
        self._service.resources.add(idempotency_table)
        self.iam.apply(DynamoDBFullAccess(idempotency_table.table))
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
