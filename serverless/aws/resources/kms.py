from troposphere import Ref, GetAtt


class EncryptableResource:
    def encryption_key_name(self):
        return "ServiceEncryptionKey"

    def encryption_key(self):
        return Ref(self.encryption_key_name())

    def encryption_alias(self):
        return "alias/${self:service}-${sls:stage}"

    def encryption_arn(self):
        return "arn:aws:kms:${aws:region}:${aws:accountId}:alias/${self:service}-${sls:stage}"
