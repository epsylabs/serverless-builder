from troposphere.sqs import Queue as SQSQueue

from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service import Identifier


class Queue(Resource, EncryptableResource):
    def __init__(self, QueueName, **kwargs):
        if "${sls:stage}" not in QueueName:
            QueueName = "${self:service}-${sls:stage}-" + QueueName

        kwargs.setdefault("KmsMasterKeyId", self.encryption_key())
        kwargs.setdefault("title", Identifier(QueueName, safe=True).pascal)

        self.queue = SQSQueue(QueueName=QueueName, **kwargs)

    def resources(self):
        return [self.queue]

    def permissions(self):
        return []

    def arn(self):
        return "arn:aws:sqs:${aws:region}:${aws:accountId}:" + self.queue.QueueName
