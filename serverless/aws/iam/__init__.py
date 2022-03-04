import abc
import hashlib
import json
from abc import ABC

from serverless.service.types import YamlOrderedDict


class PolicyBuilder(YamlOrderedDict):
    yaml_tag = "!IAM"

    def __init__(self, service=None, function=None, other=(), /, **kwds):
        super().__init__(other, **kwds)
        self.statements = []
        self._service = service
        self._function = function

    def append(self, policy):
        self.statements.append(policy)

    def allow(self, permissions, resources, sid=None):
        sid = sid or "Policy-" + str(hashlib.sha224(json.dumps([permissions, resources]).hexdigest()))
        self.statements.append(dict(Sid=sid, Effect="Allow", Action=permissions, Resource=resources))

    def deny(self, permissions, resources, sid=None):
        sid = sid or "Policy-" + str(hashlib.sha224(json.dumps([permissions, resources]).hexdigest()))
        self.statements.append(dict(Sid=sid, Effect="Deny", Action=permissions, Resource=resources))

    def apply(self, preset: "IAMPreset"):
        if self._service:
            preset.apply(self._service.provider.iam)
        else:
            preset.apply(self)

    @classmethod
    def to_yaml(cls, dumper, data):
        if data._service:
            return dumper.represent_dict(dict(role=dict(statements=data.statements)))
        else:
            return dumper.represent_list(data.statements)


class IAMPreset(ABC):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    @abc.abstractmethod
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        pass
