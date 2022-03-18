from troposphere.kms import Key, Alias

from serverless.service.plugins.kms import KMSGrant
from serverless.service.types import Feature


class Encryption(Feature):
    def __init__(self):
        super().__init__()
        self.key = Key(
            title="ServiceEncryptionKey",
            Description="Encryption Key for ${self:service}",
            Enabled=True,
            PendingWindowInDays=14,
            EnableKeyRotation=True,
            KeyPolicy={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "Enable IAM User Permissions",
                        "Effect": "Allow",
                        "Principal": {"AWS": "arn:aws:iam::${aws:accountId}:root"},
                        "Action": "kms:*",
                        "Resource": "*",
                    }
                ],
            },
        )

        self.alias = Alias(
            "ServiceEncryptionKeyAlias", AliasName="alias/${self:service}-${sls:stage}", TargetKeyId=self.key.Ref()
        )

    def enable(self, service):
        service.resources.add(self.key)
        service.resources.add(self.alias)
        service.plugins.add(KMSGrant())
