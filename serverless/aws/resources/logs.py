from troposphere.logs import LogGroup as AWSLogGroup

from serverless.aws.features.encryption import Encryption
from serverless.aws.resources import Resource
from serverless.aws.resources.kms import EncryptableResource
from serverless.service.types import Identifier


class LogGroup(Resource):
    def __init__(self, LogGroupName, **kwargs) -> None:
        kwargs.setdefault("RetentionInDays", 30)
        kwargs.setdefault("title", Identifier(LogGroupName + "LogGroup").resource)

        super().__init__(AWSLogGroup(LogGroupName=LogGroupName, **kwargs))

    def configure(self, service):
        prefix = "/services/" + service.service.spinal
        if not self.resource.LogGroupName.startswith(prefix):
            self.resource.LogGroupName = prefix + "/" + self.resource.LogGroupName.strip("/")

        if service.has(Encryption):
            self.resource.KmsKeyId = EncryptableResource.encryption_arn()

            if not service.regions:
                self.resource.DependsOn = [EncryptableResource.encryption_key_name() + "Alias"]

        super().configure(service)
