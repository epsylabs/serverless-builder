from serverless.service.types import YamlOrderedDict


class Environment(YamlOrderedDict):
    yaml_tag = "Environment"

    def __init__(self, **envs):
        super().__init__()
        self.envs = envs or {}

        if "LOG_LEVEL" in self.envs:
            self.envs["AWS_LAMBDA_LOG_LEVEL"] = self.envs["LOG_LEVEL"]
            self.envs["POWERTOOLS_LOG_LEVEL"] = self.envs["LOG_LEVEL"]

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data.envs)
