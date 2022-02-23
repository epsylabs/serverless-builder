from serverless.service.types import YamlOrderedDict


class Environment(YamlOrderedDict):
    yaml_tag = "Environment"

    def __init__(self, **envs):
        super().__init__()
        self.envs = envs or {}

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data.envs)
