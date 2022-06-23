from troposphere.dynamodb import Table

from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.aws.types import DynamoDBArn, DynamoDBIndexArn


class DynamoDBReader(IAMPreset):
    resource: Table

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan",
            ],
            resources=[
                DynamoDBArn(self.resource),
                DynamoDBIndexArn(self.resource, "*"),
            ],
            sid=sid or self.resource.name + "Reader",
        )


class DynamoDBWriter(IAMPreset):
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem",
            ],
            resources=[DynamoDBArn(self.resource)],
            sid=sid or self.resource.name + "Writer",
        )


class DynamoDBWriteOnly(IAMPreset):
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem",
            ],
            resources=[DynamoDBArn(self.resource)],
            sid=sid or self.resource.name + "WriteOnly",
        )


class DynamoDBDelete(IAMPreset):
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "dynamodb:DeleteItem",
            ],
            resources=[DynamoDBArn(self.resource)],
            sid=sid or self.resource.name + "Delete",
        )


class DynamoDBFullAccess(IAMPreset):
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:BatchWriteItem",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem",
            ],
            resources=[
                DynamoDBArn(self.resource),
                DynamoDBIndexArn(self.resource, "*"),
            ],
            sid=sid or self.resource.name + "FullAccess",
        )
