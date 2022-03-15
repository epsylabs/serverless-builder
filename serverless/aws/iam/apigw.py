import re

from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class Execute(IAMPreset):
    def __init__(self, api, endpoint):
        self.api = api
        self.endpoint = endpoint

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        if not str(self.endpoint).startswith("arn:aws:execute-api:"):
            arn = "arn:aws:execute-api:${aws:region}:${aws:accountId}:" + self.api + "/${sls:stage}/" + self.endpoint
        else:
            arn = self.endpoint

        policy_builder.allow(
            permissions=["execute-api:Invoke"],
            resources=[arn],
            sid=sid or "Invoke" + Identifier(re.sub(r"\W", "", self.endpoint)).pascal,
        )
