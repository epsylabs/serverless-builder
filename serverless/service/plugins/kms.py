from serverless.aws.resources.kms import EncryptableResource
from serverless.service.plugins.generic import Generic
from serverless.service.plugins.iam_roles import IAMRoles
from troposphere import Ref


class KMSGrant(Generic, EncryptableResource):
    def __init__(self, **kwds):
        super().__init__("serverless-kms-grants")

    def enable(self, service):
        super().enable(service)
        service.custom.kmsGrants = []

    def pre_render(self, service):
        if service.plugins.get(IAMRoles):
            for fn in service.functions.all():
                service.custom["kmsGrants"].append(dict(
                    kmsKeyId=self.encryption_key().to_dict(),
                    lambdaRoleArn=fn.iam.role_arn
                ))

        else:
            service.custom["kmsGrants"].append(dict(
                kmsKeyId=self.encryption_key().to_dict(),
                lambdaRoleArn=service.provider.iam.role_arn
            ))
