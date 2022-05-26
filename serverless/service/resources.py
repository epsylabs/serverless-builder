from typing import Union

import troposphere.ssm as ssm
import yaml
from troposphere import AWSObject

from serverless.aws.resources import Resource


class ResourceManager(yaml.YAMLObject):
    yaml_tag = "!Resources"

    def __init__(self, service, description):
        super().__init__()
        self.description = description
        self._service = service
        self.resources = []
        self.conditions = []
        self.outputs = {}

    def add(self, resource: Union[AWSObject, Resource]):
        if isinstance(resource, Resource):
            resource.configure(self._service)
            self.add_all(resource.resources())
            self._service.provider.environment.envs.update(resource.variables())

            for preset in resource.permissions():
                self._service.provider.iam.apply(preset)
        else:
            self.resources.append(resource)

        return resource

    def add_condition(self, resource: Union[AWSObject]):
        self.conditions.append(resource)

        return resource

    def add_all(self, resources):
        for resource in resources:
            self.add(resource)

    def all(self):
        return self.resources

    def output(self, output_name, name, value, append=True, export=False):
        output = {
            "Value": value
        }
        if export:
            if append:
                name = "${self:service}-${sls:stage}-" + name
            output["Export"] = {"Name": name}
        self.outputs[output_name] = output

    def export(self, output_name, name, value, append=True):
        return self.output(output_name, name, value, append, export=True)

    def parameter(self, resource_id, name, value, type="String"):
        param = self.add(ssm.Parameter(
            resource_id,
            Name=f"/services/${{self:service}}/${{sls:stage}}/{name}",
            Type=type,
            Value=""
        ))
        param.properties.__setitem__("Value", value)

        return param

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(
            dict(
                Description=data.description,
                Resources={resource.title: resource.to_dict() for resource in data.resources},
                Conditions={condition.title: condition for condition in data.conditions},
                Outputs={name: output for name, output in data.outputs.items()},
            )
        )
