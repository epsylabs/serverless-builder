from serverless.service.types import YamlOrderedDict


class Environment(YamlOrderedDict):
    yaml_tag = "Environment"

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data)
