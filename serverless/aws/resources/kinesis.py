from troposphere.kinesis import Stream, StreamEncryption

from serverless.aws.features.encryption import Encryption
from serverless.aws.iam.kinesis import KinesisReader
from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service import Identifier


class KinesisStream(Resource):
    def __init__(self, Name, **kwargs):
        if "${sls:stage}" not in Name:
            Name = "${self:service}-${sls:stage}-" + Name

        kwargs.setdefault("title", Identifier(Name, safe=True).pascal)

        super().__init__(Stream(Name=Name, **kwargs))

    def configure(self, service):
        super().configure(service)

        if service.has(Encryption) and "StreamEncryption" not in self.resource.properties:
            self.resource.StreamEncryption = StreamEncryption(
                KeyId=EncryptableResource.encryption_key(), EncryptionType="KMS"
            )

    def permissions(self):
        return [KinesisReader(self.resource.Name)]

    @property
    def Name(self):
        return self.resource.Name

    def arn(self):
        return "arn:aws:kinesis:${aws:region}:${aws:accountId}:stream/" + self.resource.Name
