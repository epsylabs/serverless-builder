from troposphere.sqs import Queue as SQSQueue

from serverless.aws.features.encryption import Encryption
from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service.types import Identifier


class Queue(Resource):
    def __init__(self, QueueName, **kwargs):
        if "${sls:stage}" not in QueueName:
            QueueName = "${self:service}-${sls:stage}-" + QueueName

        kwargs.setdefault("title", Identifier(QueueName).resource)

        super().__init__(SQSQueue(QueueName=QueueName, **kwargs))

    def configure(self, service):
        super().configure(service)

        if service.has(Encryption):
            self.resource.KmsMasterKeyId = EncryptableResource.encryption_alias()

    def permissions(self):
        return []

    def arn(self):
        return "arn:aws:sqs:${aws:region}:${aws:accountId}:" + self.resource.QueueName
