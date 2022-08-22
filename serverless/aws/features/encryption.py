from troposphere.kms import Alias, Key
from troposphere.logs import LogGroup

from serverless.service.plugins.kms import KMSGrant
from serverless.service.plugins.scriptable import Scriptable
from serverless.service.types import Feature


class Encryption(Feature):
    POLICY = {
                 "Version": "2012-10-17",
                 "Statement": [
                     {
                         "Sid": "RootPermissions",
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
             }

    def __init__(self):
        super().__init__()
        self.key = Key(
            title="ServiceEncryptionKey",
            Description="Encryption Key for ${self:service}",
            Enabled=True,
            PendingWindowInDays=14,
            EnableKeyRotation=True,
            KeyPolicy=Encryption.POLICY
        )

        self.alias = Alias(
            "ServiceEncryptionKeyAlias", AliasName="alias/${self:service}-${sls:stage}", TargetKeyId=self.key.Ref()
        )

    def pre_render(self, service):
        super().pre_render(service)

        if service.regions:
            if not service.plugins.has(Scriptable):
                service.plugins.add(Scriptable())

            # service.plugins.get(Scriptable).hooks.append("")

            return

        for resource in service.resources.all():
            if resource.title == "ServiceSecret":
                resource.DependsOn = "ServiceEncryptionKeyAlias"

        for fn in service.functions.all():
            self.key.KeyPolicy["Statement"].append(self.create_log_group_kms_statement("arn:aws:logs:${aws:region}:${aws:accountId}:log-group:/aws/lambda/" + fn.name.spinal))

        for resource in service.resources.all():
            if isinstance(resource, LogGroup):
                if resource.properties.get("KmsKeyId") is not None:
                    self.key.KeyPolicy["Statement"].append(self.create_log_group_kms_statement("arn:aws:logs:${aws:region}:${aws:accountId}:log-group:" + resource.LogGroupName))

    def create_log_group_kms_statement(self, log_group):
        return {
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
                    "kms:EncryptionContext:aws:logs:arn": log_group
                }
            },
        }

    def enable(self, service):
        if not service.regions:
            service.resources.add(self.key)
            service.resources.add(self.alias)

        service.plugins.add(KMSGrant())
