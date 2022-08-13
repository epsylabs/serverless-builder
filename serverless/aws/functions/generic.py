from __future__ import annotations

from typing import Optional

from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.dynamodb import AttributeDefinition, KeySchema, TimeToLiveSpecification

from serverless.aws.features.encryption import Encryption
from serverless.aws.iam import FunctionPolicyBuilder
from serverless.aws.resources import DummyResource
from serverless.aws.resources.dynamodb import Table
from serverless.aws.resources.kms import EncryptableResource
from serverless.aws.resources.sqs import Queue
from serverless.aws.types import SQSArn
from serverless.service.environment import Environment
from serverless.service.plugins.iam_roles import IAMRoles
from serverless.service.plugins.lambda_dlq import LambdaDLQ
from serverless.service.plugins.python_requirements import PythonRequirements
from serverless.service.types import Identifier, YamlOrderedDict


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
        use_dlq=False,
        use_async_dlq=False,
        **kwargs,
    ):
        super().__init__()
        self._service = service

        self.key = Identifier(name)
        self.name = (
            force_name
            if force_name
            else Identifier(self._service.service.spinal.lower() + "-${sls:stage}" + "-" + self.key.spinal.lower())
        )
        self.description = description

        if not handler:
            handler = f"{self._service.service.snake}.{self.key.snake}.handler"

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

        self._service.resources.export(self.resource_name() + "ArnOutput",  self.name.spinal + "-arn", self.arn(), append=False)

        if layers:
            self.layers = layers

        if timeout:
            self.timeout = timeout

        if idempotency:
            self.with_idempotency(idempotency)

        for name, value in kwargs.items():
            setattr(self, name, value)

        self.dlq = None

        if use_dlq:
            self.use_dlq()

        if use_async_dlq:
            self.use_async_dlq()

        log_group = dict(Type="AWS::Logs::LogGroup", Properties=dict(RetentionInDays=30))
        if service.has(Encryption):
            log_group["Properties"]["KmsKeyId"] = EncryptableResource.encryption_arn()
            if not service.regions:
                log_group["DependsOn"] = [EncryptableResource.encryption_key_name() + "Alias"]

        service.resources.add(DummyResource(title=self.log_group_name(), **log_group))

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

    def log_group_name(self):
        return f"{self.key.pascal}LogGroup"

    def iam_role_name(self):
        return f"{self.key.pascal}IamRoleLambdaExecution"

    def resource_name(self):
        return f"{self.key.pascal}LambdaFunction"

    def trigger(self, event):
        self.events.append(event)

        return event

    def apply(self, **kwargs):
        for event in self.events:
            for k, v in kwargs.items():
                event[k] = v

    def use_dlq(self, onErrorDLQArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> Function:
        """
        @param onErrorDLQArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """

        if not self._service.plugins.has(LambdaDLQ):
            self._service.plugins.add(LambdaDLQ())

        if not onErrorDLQArn:
            onErrorDLQArn = self._ensure_dlq(MessageRetentionPeriod).get("arn")

        self.deadLetter = dict(targetArn=onErrorDLQArn)

        return self

    def use_async_dlq(self, onFailuredlqArn: Optional[str] = None, MessageRetentionPeriod: int = 1209600) -> Function:
        """
        @param onFailuredlqArn: Optional[str]
        @param MessageRetentionPeriod: integer – defaults to 14 days in seconds
        @return None
        """
        if not onFailuredlqArn:
            onFailuredlqArn = self._ensure_dlq(MessageRetentionPeriod).get("arn")

        self.destinations = dict(onFailure=onFailuredlqArn)

        return self

    def _ensure_dlq(self, MessageRetentionPeriod):
        name = f"{self.name.spinal}-dlq"
        resource = f"{self.name.resource}DLQ"
        if self.dlq:
            return {"Ref": resource, "arn": SQSArn(name)}

        self.dlq = Queue(
            title=resource,
            QueueName=name,
            MessageRetentionPeriod=MessageRetentionPeriod,
        )
        self._service.resources.add(self.dlq)

        self.iam.allow(
            sid=f"{self.name.resource}DLQWriter",
            permissions=["sqs:GetQueueUrl", "sqs:SendMessage"],
            resources=[self.dlq.arn()],
        )

        self._service.resources.add(
            Alarm(
                f"{self.name.resource}DLQAlarm",
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

        self.dependsOn = [
            self.iam_role_name(),
            self.log_group_name(),
            resource,
        ]

        return {"Ref": f"{self.name.pascal}DLQ", "arn": SQSArn(name)}

    def with_vpc(self, security_group_names=None, subnet_names=None):
        if security_group_names:
            self.vpcDiscovery = dict(securityGroups=[dict(tagKey="Name", tagValues=security_group_names.copy())])

        return self

    def with_idempotency(self, table_name=None):
        table_name = table_name or f"{self.name.pascal.replace('${sls:stage}', '')}Idempotency-" + '${sls:stage}'

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
        ).with_full_access()
        self._service.resources.add(idempotency_table)
        env = self.get("environment", Environment())
        env.envs["IDEMPOTENCY_TABLE"] = idempotency_table.resource.TableName
        self.environment = env

        return self

    @classmethod
    def to_yaml(cls, dumper, data):
        events = data.events
        data.pop("_service", None)
        data.pop("key", None)
        data.pop("dlq", None)

        if not data.events:
            del data["events"]
        else:
            data.events = [{event.yaml_tag: event} for event in events]

        return dumper.represent_dict(data)
