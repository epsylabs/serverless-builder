from serverless.aws.iam import IAMPreset


class SecretsManagerReader(IAMPreset):
    def __init__(self, resource):
        super().__init__(resource)

    def apply(self, service):
        service.provider.iam.allow(
            "secretsmanager",
            ["secretsmanager:GetSecretValue"],
            "arn:aws:secretsmanager:${aws:region}:${aws:accountId}:secret:" + self.resource,
        )
