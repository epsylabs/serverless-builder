import yaml
from troposphere import AWSObject


class ResourceManager(yaml.YAMLObject):
    yaml_tag = "!Resources"

    def __init__(self, service, description):
        super().__init__()
        self.description = description
        self._service = service
        self.resources = []

    def add(self, resource: AWSObject):
        # resource.validate()
        self.resources.append(resource)

    def add_all(self, resources):
        for resource in resources:
            self.add(resource)

    def all(self):
        return self.resources

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(
            dict(
                Description=data.description,
                Resources={resource.title: resource.to_dict() for resource in data.resources},
            )
        )
