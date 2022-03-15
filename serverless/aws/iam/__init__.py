import abc
import hashlib
import json
from abc import ABC

from serverless.service.types import YamlOrderedDict


class PolicyBuilder(YamlOrderedDict):
    yaml_tag = "!IAM"

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.statements = []

    def append(self, policy):
        self.statements.append(policy)

    def allow(self, permissions, resources, sid=None):
        sid = sid or "Policy-" + str(hashlib.sha224(json.dumps([permissions, resources]).hexdigest()))
        self.statements.append(dict(Sid=sid, Effect="Allow", Action=permissions, Resource=resources))

    def deny(self, permissions, resources, sid=None):
        sid = sid or "Policy-" + str(hashlib.sha224(json.dumps([permissions, resources]).hexdigest()))
        self.statements.append(dict(Sid=sid, Effect="Deny", Action=permissions, Resource=resources))

    def apply(self, preset: "IAMPreset"):
        preset.apply(self)

    @property
    def role_arn(self):
        return "arn:aws:iam::${{ aws:accountId }}:role/" + self.role

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_list(data.statements)


class ServicePolicyBuilder(PolicyBuilder):
    yaml_tag = "!IAM"

    @property
    def role(self):
        if self.name:
            return self.name

        return f"IamRoleLambdaExecution"

    @classmethod
    def to_yaml(cls, dumper, data):
        export = dict(data.items())

        return dumper.represent_dict(dict(role=export))


class FunctionPolicyBuilder(PolicyBuilder):
    yaml_tag = "!IAM"

    def __init__(self, function_name, **kwds):
        super().__init__(**kwds)
        self.function_name = function_name

    @property
    def role(self):
        return f"${{ self:service }}-${{ sls:stage }}-{self.function_name}-${{ aws:region }}-lambdaRole"


class IAMPreset(ABC):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    @abc.abstractmethod
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        pass
