from troposphere.kinesis import Stream, StreamEncryption

from serverless.aws.iam.kinesis import KinesisReader
from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service import Identifier


class KinesisStream(Resource, EncryptableResource):
    def __init__(self, Name, **kwargs):
        if "${sls:stage}" not in Name:
            Name = "${self:service}-${sls:stage}-" + Name

        kwargs.setdefault("title", Identifier(Name, safe=True).pascal)
        kwargs.setdefault("StreamEncryption", StreamEncryption(KeyId=self.encryption_key(), EncryptionType="KMS"))

        self.stream = Stream(Name=Name, **kwargs)

    def resources(self):
        return [self.stream]

    def permissions(self):
        return [KinesisReader(self.stream.Name)]

    @property
    def Name(self):
        return self.stream.Name

    def arn(self):
        return "arn:aws:kinesis:${aws:region}:${aws:accountId}:stream/" + self.stream.Name
