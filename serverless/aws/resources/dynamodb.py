from troposphere.dynamodb import PointInTimeRecoverySpecification, SSESpecification, GlobalTable, ReplicaSpecification, \
    ReplicaSSESpecification, StreamSpecification, GlobalTableSSESpecification
from troposphere.dynamodb import Table as DynamoDBTable, GlobalTable

from serverless.aws.iam.dynamodb import (
    DynamoDBDelete,
    DynamoDBFullAccess,
    DynamoDBReader,
    DynamoDBWriteOnly,
    DynamoDBWriter,
)
from ..types import Ref, Equals

from ...service import Identifier
from ..features.encryption import Encryption
from ..iam import IAMPreset, PolicyBuilder
from . import Resource
from .kms import EncryptableResource


class Table(Resource):
    def __init__(self, TableName, with_full_access=False, with_read_access=False, is_global=False, **kwargs):
        if "${sls:stage}" not in TableName:
            TableName += "-${sls:stage}"

        kwargs.setdefault("DeletionPolicy", "Retain")

        if is_global:
            cls = GlobalTable
            kwargs["Condition"] = "IsPrimaryRegion"
        else:
            cls = DynamoDBTable
            kwargs.setdefault(
                "PointInTimeRecoverySpecification", PointInTimeRecoverySpecification(PointInTimeRecoveryEnabled=True)
            )

        self.PointInTimeRecoverySpecification = kwargs.get(
            "PointInTimeRecoverySpecification", PointInTimeRecoverySpecification(PointInTimeRecoveryEnabled=True)
        )

        super().__init__(
            cls(title=TableName.replace("${sls:stage}", "").strip("-"), TableName=TableName, **kwargs)
        )
        self.access = None
        self.is_global = is_global

        if with_full_access:
            self.with_full_access()

        if with_read_access:
            self.with_read_access()

    def configure(self, service):
        if service.regions and self.is_global:
            self.resource.Replicas = [ReplicaSpecification(Region=region, PointInTimeRecoverySpecification=self.PointInTimeRecoverySpecification) for region in service.regions]
            self.resource.StreamSpecification = StreamSpecification(StreamViewType="NEW_AND_OLD_IMAGES")

        if service.has(Encryption):
            sse_kwargs = dict(SSEEnabled=True, SSEType="KMS")

            if not isinstance(self.resource, GlobalTable):
                sse_kwargs["KMSMasterKeyId"] = EncryptableResource.encryption_key()
            else:
                for replica in self.resource.Replicas:
                    replica.SSESpecification = ReplicaSSESpecification(KMSMasterKeyId=EncryptableResource.encryption_alias())

            cls = GlobalTableSSESpecification if self.is_global else SSESpecification
            self.resource.SSESpecification = cls(**sse_kwargs)
            if not service.regions:
                self.resource.DependsOn = ["ServiceEncryptionKeyAlias"]

        if isinstance(self.resource, GlobalTable):
            service.resources.conditions.append(Equals("IsPrimaryRegion", [Ref("AWS::Region"), service.regions[0]]))

        if service.service.pascal not in self.resource.TableName:
            self.resource.TableName = service.service.pascal + self.resource.TableName

    def _apply(self, preset: IAMPreset, builder: PolicyBuilder = None):
        if builder:
            builder.apply(preset)
        else:
            self.access = preset

        return self

    def with_full_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBFullAccess(self.resource), builder)

    def with_read_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBReader(self.resource), builder)

    def with_write_access(self, builder: PolicyBuilder = None):
        return self._apply(DynamoDBWriter(self.resource), builder)

    def enable_read(self, builder: PolicyBuilder):
        return self.with_read_access(builder)

    def enable_write(self, builder: PolicyBuilder):
        return self._apply(DynamoDBWriteOnly(self.resource), builder)

    def enable_delete(self, builder: PolicyBuilder):
        return self._apply(DynamoDBDelete(self.resource), builder)

    @property
    def table_arn(self):
        return Table.arn(self.resource)

    @classmethod
    def arn(cls, resource):
        return f"arn:aws:dynamodb:${{aws:region}}:${{aws:accountId}}:table/{resource.TableName}"

    def variables(self):
        return {
            "TABLE_"
            + Identifier(
                self.resource.TableName.replace("-${sls:stage}", "").replace("${sls:stage}", "")
            ).snake.upper(): self.resource.TableName
        }

    def resources(self):
        return [self.resource]

    def permissions(self):
        if self.access:
            return [self.access]
        return []
