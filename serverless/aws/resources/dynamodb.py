from troposphere.dynamodb import Table as DynamoDBTable

from . import Resource
from serverless.aws.iam.dynamodb import DynamoDBFullAccess, DynamoDBReader, DynamoDBWriter


class Table(Resource):
    def __init__(self, TableName, **kwargs):
        if "${sls:stage}" not in TableName:
            TableName += "-${sls:stage}"

        self.table = DynamoDBTable(
            title=TableName.replace("${sls:stage}", "").strip("-"), TableName=TableName, **kwargs
        )
        self.access = None

    def with_full_access(self):
        self.access = DynamoDBFullAccess(self.table)

        return self

    def with_read_access(self):
        self.access = DynamoDBReader(self.table)

        return self

    def with_write_access(self):
        self.access = DynamoDBWriter(self.table)

        return self

    @property
    def table_arn(self):
        return self.table.Ref().to_dict()

    def resources(self):
        return [self.table]

    def permissions(self):
        return [self.access]
