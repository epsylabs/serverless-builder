from troposphere import Ref


class EncryptableResource:
    def encryption_key(self):
        return Ref("ServiceEncryptionKey")

    def encryption_alias(self):
        return "alias/${self:service}-${sls:stage}"
