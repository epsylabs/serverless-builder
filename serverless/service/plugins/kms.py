from serverless.service.plugins.generic import Generic
from serverless.service.plugins.iam_roles import IAMRoles
from troposphere import Ref


class KMSGrant(Generic):
    def __init__(self, **kwds):
        super().__init__("serverless-kms-grants")

    def enable(self, service):
        super().enable(service)
        service.custom.kmsGrants = []

    def pre_render(self, service):
        if service.plugins.get(IAMRoles):
            for fn in service.functions.all():
                service.custom["kmsGrants"].append(dict(
                    kmsKeyId="",
                    lambdaRoleArn=Ref(fn.role).to_dict()
                ))

        else:
            service.custom["kmsGrants"].append(dict(
                kmsKeyId="alias/${self:service}",
                lambdaRoleArn=Ref(service.provider.iam.role).to_dict()
            ))
