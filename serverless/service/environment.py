from serverless.service.types import YamlOrderedDict


class Environment(YamlOrderedDict):
    yaml_tag = "Environment"

    def __init__(self, envs=None):
        super().__init__()
        if envs:
            self.envs = envs

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data.envs)
