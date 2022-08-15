import hashlib

from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class SQSPublisher(IAMPreset):
    def __init__(self, resource):
        super().__init__(resource)

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=["sqs:SendMessage"],
            resources=str(self.resource),
            sid="SQSPublisherI" + hashlib.sha224(str(self.resource).encode("ascii")).hexdigest(),
        )
