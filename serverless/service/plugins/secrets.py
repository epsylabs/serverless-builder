from serverless.aws.resources.kms import EncryptableResource
from serverless.service.plugins.generic import Generic
from troposphere.secretsmanager import Secret


class KMSSecrets(Generic, EncryptableResource):
    yaml_tag = "!AWSSecretsPlugin"

    def __init__(self, secrets):
        super().__init__("serverless-secrets-mgr-plugin")
        self.secrets = secrets or []

    def enable(self, service):
        secret = "/service/${self:service}/${opt:stage}"
        service.custom.secrets = dict(secretId=secret, variableNames=self.secrets)

        service.resources.add(Secret(title="ServiceSecret", KmsKeyId=self.encryption_key(), Name=secret))
