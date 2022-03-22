from troposphere.iam import Role as IAMRole, Policy

from serverless.aws.iam import PolicyBuilder
from serverless.aws.resources import Resource
from serverless.service import Identifier


class Role(Resource):
    def __init__(self, RoleName, **kwargs):
        self.role = IAMRole(
            title=Identifier(RoleName, safe=True).pascal,
            RoleName=RoleName,
            Policies=[Policy(PolicyName=RoleName + "-inline", PolicyDocument=dict())],
            validation=False,
            **kwargs
        )

        if "${self:service}" not in RoleName:
            self.role.properties.__setitem__("RoleName", "${self:service}-${sls:stage}-${aws:region}" + RoleName)
        self.policy = PolicyBuilder()

    def resources(self):
        self.role.Policies[0].PolicyDocument = dict(Statement=self.policy.statements)
        return super().resources() + [self.role]
