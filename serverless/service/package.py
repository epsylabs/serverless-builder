import yaml


class Package(yaml.YAMLObject):
    yaml_tag = "!Package"

    def __init__(self, patterns):
        super().__init__()
        self.patterns = patterns

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict({"patterns": data.patterns})
