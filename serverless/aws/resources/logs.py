from troposphere.logs import LogGroup as AWSLogGroup

from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service.types import Identifier


class LogGroup(Resource, EncryptableResource):
    def __init__(self, LogGroupName, **kwargs) -> None:
        kwargs.setdefault("RetentionInDays", 30)
        kwargs.setdefault("KmsKeyId", self.encryption_arn())
        kwargs.setdefault("title", Identifier(LogGroupName + "LogGroup").resource)
        kwargs.setdefault("DependsOn", [self.encryption_key_name() + "Alias"])

        super().__init__(AWSLogGroup(LogGroupName=LogGroupName, **kwargs))

    def configure(self, service):
        prefix = "/services/" + service.service.spinal
        if not self.resource.LogGroupName.startswith(prefix):
            self.resource.LogGroupName = prefix + "/" + self.resource.LogGroupName.strip("/")

        super().configure(service)
