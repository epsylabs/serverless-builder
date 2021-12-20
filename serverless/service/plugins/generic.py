from serverless.service.types import YamlOrderedDict


class Generic(YamlOrderedDict):
    yaml_tag = "!GenericPlugin"

    def __init__(self, name, other=(), /, **kwds):
        super().__init__(other, **kwds)
        self.name = name

    def enable(self, service):
        pass

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_str(data.name)
