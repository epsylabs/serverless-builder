from troposphere.dynamodb import Table as DynamoDBTable, PointInTimeRecoverySpecification, SSESpecification

from serverless.aws.iam.dynamodb import (
    DynamoDBFullAccess,
    DynamoDBReader,
    DynamoDBWriter,
    DynamoDBDelete,
    DynamoDBWriteOnly,
)
from . import Resource
from .kms import EncryptableResource
from ..iam import PolicyBuilder, IAMPreset
from ...service import Identifier


class Table(Resource, EncryptableResource):
    def __init__(self, TableName, with_full_access=False, with_read_access=False, **kwargs):
        if "${sls:stage}" not in TableName:
            TableName += "-${sls:stage}"

        kwargs.setdefault(
            "PointInTimeRecoverySpecification", PointInTimeRecoverySpecification(PointInTimeRecoveryEnabled=True)
        )
        kwargs.setdefault(
            "SSESpecification",
            SSESpecification(KMSMasterKeyId=self.encryption_key(), SSEEnabled=True, SSEType="KMS"),
        )

        kwargs.setdefault("DeletionPolicy", "Retain")

        self.table = DynamoDBTable(
            title=TableName.replace("${sls:stage}", "").strip("-"), TableName=TableName, **kwargs
        )
        self.access = None

        if with_full_access:
            self.with_read_access()

        if with_read_access:
            self.with_read_access()

    def configure(self, service):
        if service.service.pascal not in self.table.TableName:
            self.table.TableName = service.service.pascal + self.table.TableName

    def _apply(self, preset: IAMPreset, builder: PolicyBuilder = None):
        if builder:
            builder.apply(preset)
        else:
            self.access = preset

        return self

    def with_full_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBFullAccess(self.table), builder)

    def with_read_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBReader(self.table), builder)

    def with_write_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBWriter(self.table), builder)

    def enable_read(self, builder: PolicyBuilder):
        return self.with_read_access(builder)

    def enable_write(self, builder: PolicyBuilder):
        return self._apply(DynamoDBWriteOnly(self.table), builder)

    def enable_delete(self, builder: PolicyBuilder):
        return self._apply(DynamoDBDelete(self.table), builder)

    @property
    def table_arn(self):
        return self.table.Ref().to_dict()

    def variables(self):
        return {
            "TABLE_" + Identifier(self.table.TableName.replace("-${sls:stage}", "")).snake.upper(): self.table.TableName
        }

    def resources(self):
        return [self.table]

    def permissions(self):
        if self.access:
            return [self.access]
        return []
