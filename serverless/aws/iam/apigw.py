from serverless.aws.iam import IAMPreset


class Execute(IAMPreset):
    def __init__(self, api, endpoint):
        self.api = api
        self.endpoint = endpoint

    def apply(self, service, sid=None):
        if not sid:
            sid = f"Invoke"

        if not str(self.endpoint).startswith("arn:aws:execute-api:"):
            arn = "arn:aws:execute-api:${aws:region}:${aws:accountId}:" + self.api + "/${sls:stage}/" + self.endpoint
        else:
            arn = self.endpoint

        service.provider.iam.allow(
            sid,
            ["execute-api:Invoke"],
            [arn],
        )
