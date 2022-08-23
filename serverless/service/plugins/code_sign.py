from serverless.service.plugins.generic import Generic


class AWSCodeSign(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-aws-signer
    """

    yaml_tag = "!AWSSignPlugin"

    def __init__(
        self,
        profile,
        sign_policy="Enforce",
        source_bucket=None,
        source_key=None,
        destination_bucket=None,
        destination_prefix=None,
        retain=True,
    ):
        super().__init__("serverless-aws-signer")
        self.profile = profile
        self.sign_policy = sign_policy
        self.source_bucket = source_bucket
        self.source_key = source_key
        self.destination_bucket = destination_bucket
        self.destination_prefix = destination_prefix or "signed-"
        self.retain = retain

    def enable(self, service):
        service.custom.signer = dict(
            retain=self.retain,
            source=dict(
                s3=dict(
                    bucketName=self.source_bucket or service.provider.deploymentBucket.get("name"),
                    key=self.source_key or f"{service.service.spinal}.zip",
                )
            ),
            destination=dict(
                s3=dict(
                    bucketName=self.destination_bucket or service.provider.deploymentBucket.get("name"),
                    prefix=self.destination_prefix,
                )
            ),
            profileName=self.profile,
            signingPolicy=self.sign_policy,
        )
