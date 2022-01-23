import abc
from abc import ABC

from serverless.service.types import YamlOrderedDict


class IAMPreset(ABC):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    @abc.abstractmethod
    def apply(self, service):
        pass


class IAMManager(YamlOrderedDict):
    yaml_tag = "!IAM"

    def __init__(self, service, other=(), /, **kwds):
        super().__init__(other, **kwds)
        self.statements = []
        self._service = service

    def allow(self, sid, permissions, resources):
        self.statements.append(dict(Sid=sid, Effect="Allow", Action=permissions, Resource=resources))

    def deny(self, sid, permissions, resources):
        self.statements.append(dict(Sid=sid, Effect="Deny", Action=permissions, Resource=resources))

    def apply(self, preset: IAMPreset):
        preset.apply(self._service)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(dict(role=dict(statements=data.statements)))
