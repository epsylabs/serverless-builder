from troposphere.secretsmanager import Secret

from serverless.aws.resources.kms import EncryptableResource
from serverless.service.plugins.generic import Generic


class KMSSecrets(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-secrets-mgr-plugin
    """

    yaml_tag = "!AWSSecretsPlugin"

    def __init__(self, secrets):
        super().__init__("serverless-secrets-mgr-plugin")
        self.secrets = secrets or []

    def enable(self, service):
        secret = "/service/${self:service}/${opt:stage}"
        service.custom.secrets = dict(secretId=secret, variableNames=self.secrets)

        service.resources.add(Secret(title="ServiceSecret", KmsKeyId=EncryptableResource.encryption_key(), Name=secret))
