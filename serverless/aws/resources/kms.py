from troposphere import GetAtt, Ref


class EncryptableResource:
    @staticmethod
    def encryption_key_name():
        return "ServiceEncryptionKey"

    @staticmethod
    def encryption_key():
        return Ref(EncryptableResource.encryption_key_name())

    @staticmethod
    def encryption_alias():
        return "alias/${self:service}-${sls:stage}"

    @staticmethod
    def encryption_arn():
        return "arn:aws:kms:${aws:region}:${aws:accountId}:alias/${self:service}-${sls:stage}"
