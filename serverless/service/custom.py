from serverless.service.types import YamlOrderedDict


class Custom(YamlOrderedDict):
    yaml_tag = "Custom"

    def __init__(self, **kwargs):
        super().__init__()
        self.custom = kwargs or {}

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data.custom)
