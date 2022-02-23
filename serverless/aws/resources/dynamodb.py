from troposphere.dynamodb import Table as DynamoDBTable

from . import Resource
from serverless.aws.iam.dynamodb import DynamoDBFullAccess, DynamoDBReader, DynamoDBWriter


class Table(Resource):
    def __init__(self, TableName, **kwargs):
        self.table = DynamoDBTable(title=TableName, TableName=TableName, **kwargs)
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

    def resources(self):
        return [self.table]

    def permissions(self):
        return [self.access]
