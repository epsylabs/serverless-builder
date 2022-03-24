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
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "logs.${aws:region}.amazonaws.com"},
                        "Action": [
                            "kms:Encrypt*",
                            "kms:Decrypt*",
                            "kms:ReEncrypt*",
                            "kms:GenerateDataKey*",
                            "kms:Describe*",
                        ],
                        "Resource": "*",
                        "Condition": {
                            "ArnLike": {
                                "kms:EncryptionContext:aws:logs:arn": "arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/services/${self:service}/*"
                            }
                        },
                    },
                ],
            },
        )

        self.alias = Alias(
            "ServiceEncryptionKeyAlias", AliasName="alias/${self:service}-${sls:stage}", TargetKeyId=self.key.Ref()
        )

    def pre_render(self, service):
        super().pre_render(service)
        for fn in service.functions.all():
            self.key.KeyPolicy["Statement"].append({
                "Effect": "Allow",
                "Principal": {"Service": "logs.${aws:region}.amazonaws.com"},
                "Action": [
                    "kms:Encrypt*",
                    "kms:Decrypt*",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:Describe*",
                ],
                "Resource": "*",
                "Condition": {
                    "ArnLike": {
                        "kms:EncryptionContext:aws:logs:arn": "arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/" + fn.name.spinal
                    }
                },
            })

    def enable(self, service):
        service.resources.add(self.key)
        service.resources.add(self.alias)
        service.plugins.add(KMSGrant())
