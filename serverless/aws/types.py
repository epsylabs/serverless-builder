import yaml

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


class DynamoDBArn(GenericArn):
    yaml_tag = "!Arn"

    def __init__(self, table):
        self.table = table

    def __str__(self):
        return f"arn:aws:dynamodb:${{aws:region}}:${{aws:accountId}}:table/{self.table.TableName}"


class DynamoDBIndexArn(GenericArn):
    yaml_tag = "!Arn"

    def __init__(self, table, index="*"):
        self.table = table
        self.index = index

    def __str__(self):
        return f"arn:aws:dynamodb:${{aws:region}}:${{aws:accountId}}:table/{self.table.TableName}/index/{self.index}"


class EventBridgeBusArn(GenericArn):
    yaml_tag = "!Arn"

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"arn:aws:events:${{aws:region}}:${{aws:accountId}}:event-bus/{self.name}"


class Ref(yaml.YAMLObject):
    yaml_tag = "!Ref"

    def __init__(self, data):
        self.data = data

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict({"Ref": data.data})


class Equals(yaml.YAMLObject):
    yaml_tag = "!Equals"

    def __init__(self, title, data):
        self.title = title
        self.data = data

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict({"Fn::Equals": data.data})
