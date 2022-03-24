from troposphere.logs import LogGroup as AWSLogGroup

from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service.types import Identifier


class LogGroup(Resource, EncryptableResource):
    def __init__(self, LogGroupName, **kwargs) -> None:
        kwargs.setdefault("RetentionInDays", 30)
        kwargs.setdefault("KmsKeyId", self.encryption_alias())
        kwargs.setdefault("title", Identifier(LogGroupName + "LogGroup").resource)

        super().__init__(AWSLogGroup(LogGroupName=LogGroupName, **kwargs))
