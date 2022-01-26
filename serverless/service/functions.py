import yaml


class FunctionManager(yaml.YAMLObject):
    yaml_tag = "!Functions"

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.functions = []

    def add(self, function):
        self.functions.append(function)

    def all(self):
        return self.functions

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict({function.key: function for function in data.functions})
