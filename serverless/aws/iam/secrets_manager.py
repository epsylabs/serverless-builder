import re

from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class SecretsManagerReader(IAMPreset):
    def __init__(self, resource):
        super().__init__(resource)

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        resource = str(self.resource) if self.resource.endswith("-??????") else f"{self.resource}-??????"

        policy_builder.allow(
            permissions=["secretsmanager:GetSecretValue"],
            resources="arn:aws:secretsmanager:${aws:region}:${aws:accountId}:secret:" + resource,
            sid="SecretsManager" + Identifier(re.sub(r"\W", "", self.resource)).pascal,
        )
