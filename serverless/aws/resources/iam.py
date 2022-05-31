from troposphere.iam import Policy
from troposphere.iam import Role as IAMRole

from serverless.aws.iam import PolicyBuilder
from serverless.aws.resources import Resource
from serverless.service import Identifier
from serverless.service.types import ResourceName, ResourceId


class Role(Resource):
    def __init__(self, RoleName, **kwargs):
        self.role = IAMRole(
            title=str(ResourceId(RoleName)),
            RoleName=RoleName,
            Policies=[Policy(PolicyName=RoleName + "-inline", PolicyDocument=dict())],
            validation=False,
            **kwargs
        )

        if "${self:service}" not in RoleName:
            self.role.properties.__setitem__("RoleName", str(ResourceName("${self:service}-${sls:stage}-${aws:region}-" + RoleName)))

        self.policy = PolicyBuilder()

    def resources(self):
        self.role.Policies[0].PolicyDocument = dict(Statement=self.policy.statements)
        return [self.role]
