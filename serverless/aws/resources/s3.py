from troposphere.s3 import Bucket, Private, BucketEncryption, ServerSideEncryptionRule, ServerSideEncryptionByDefault, \
    PublicAccessBlockConfiguration, VersioningConfiguration
from serverless.aws.resources import Resource

from serverless.aws.resources.kms import EncryptableResource
from serverless.service import Identifier


class S3Bucket(Resource, EncryptableResource):
    def __init__(self, BucketName="${self:service}", domain=None, **kwargs):
        kwargs.setdefault("AccessControl", "Private")

        kwargs.setdefault(
            "BucketEncryption",
            BucketEncryption(
                ServerSideEncryptionConfiguration=[ServerSideEncryptionRule(
                    BucketKeyEnabled=True,
                    ServerSideEncryptionByDefault=ServerSideEncryptionByDefault(
                        KMSMasterKeyID=self.encryption_key(),
                        SSEAlgorithm="aws:kms"
                    )
                )]
            ),
        )

        kwargs.setdefault("PublicAccessBlockConfiguration", PublicAccessBlockConfiguration(
            BlockPublicAcls=True,
            BlockPublicPolicy=True,
            IgnorePublicAcls=True,
            RestrictPublicBuckets=True,
        ))

        kwargs.setdefault("VersioningConfiguration", VersioningConfiguration(
            Status="Enabled"
        ))

        self.bucket = Bucket(title=Identifier(BucketName, safe=True).pascal, **kwargs)

        self.bucket.properties.__setitem__(
            "BucketName", BucketName + ".${aws:region}." + (domain or "${ssm:/global/primary-domain}")
        )

    def resources(self):
        return super().resources() + [self.bucket]
