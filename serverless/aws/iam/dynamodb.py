from troposphere.dynamodb import Table

from serverless.aws.iam import IAMPreset


class DynamoDBReader(IAMPreset):
    resource: Table

    def apply(self, service, sid=None):
        if not sid:
            sid = self.resource.name+"Reader"
        service.provider.iam.allow(
            sid,
            [
                "dynamodb:Query",
                "dynamodb:GetItem",
            ],
            [self.resource.get_att("Arn").to_dict()],
        )


class DynamoDBWriter(IAMPreset):
    def apply(self, service, sid=None):
        if not sid:
            sid = self.resource.name+"Writer"
        service.provider.iam.allow(
            sid,
            [
                "dynamodb:BatchWriteItem",
                "dynamodb:CreateTable",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem"
            ],
            [self.resource.get_att("Arn").to_dict()],
        )
