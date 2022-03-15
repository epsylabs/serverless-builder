from troposphere import Ref


class EncryptableResource:
    def encryption_key(self):
        return Ref("ServiceEncryptionKey")
