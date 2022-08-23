from typing import final
from troposphere.s3 import (
    Bucket,
    BucketEncryption,
    Private,
    PublicAccessBlockConfiguration,
    ServerSideEncryptionByDefault,
    ServerSideEncryptionRule,
    VersioningConfiguration,
)

from serverless.aws.features.encryption import Encryption
from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service import Identifier


class S3Bucket(Resource):
    def __init__(self, BucketName="${self:service}", domain=None, ForceName=False, **kwargs):
        kwargs.setdefault("AccessControl", "Private")

        kwargs.setdefault(
            "PublicAccessBlockConfiguration",
            PublicAccessBlockConfiguration(
                BlockPublicAcls=True,
                BlockPublicPolicy=True,
                IgnorePublicAcls=True,
                RestrictPublicBuckets=True,
            ),
        )

        kwargs.setdefault("VersioningConfiguration", VersioningConfiguration(Status="Enabled"))

        bucket = Bucket(title=Identifier(BucketName, safe=True).pascal, **kwargs)

        final_name = BucketName + ".${aws:region}." + (domain or "${ssm:/global/primary-domain}")
        if ForceName:
            final_name = BucketName

        bucket.properties.__setitem__(
            "BucketName", final_name
        )

        super().__init__(bucket)

    def configure(self, service):
        super().configure(service)

        if service.has(Encryption) and getattr(self.resource, "BucketEncryption", None) is None:
            self.resource.BucketEncryption = BucketEncryption(
                ServerSideEncryptionConfiguration=[
                    ServerSideEncryptionRule(
                        BucketKeyEnabled=True,
                        ServerSideEncryptionByDefault=ServerSideEncryptionByDefault(
                            KMSMasterKeyID=EncryptableResource.encryption_key(), SSEAlgorithm="aws:kms"
                        ),
                    )
                ]
            )
