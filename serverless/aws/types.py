from serverless.service import YamlOrderedDict


class GenericArn(YamlOrderedDict):
    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_str(str(data))


class SQSArn(GenericArn):
    yaml_tag = "!Arn"

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"arn:aws:sqs:${{aws:region}}:${{aws:accountId}}:{self.name}"


class EventBridgeBusArn(GenericArn):
    yaml_tag = "!Arn"

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"arn:aws:events:${{aws:region}}:${{aws:accountId}}:event-bus/{self.name}"
