from serverless.service import YamlOrderedDict


class CognitoAuth(YamlOrderedDict):
    yaml_tag = "!CognitoAuth"

    def __init__(self, arn=None, pool=None):
        self.name = "Cognito"
        if arn:
            self.arn = arn
        if pool:
            self.arn = f"arn:aws:cognito-idp:${{aws:region}}:${{aws:accountId}}:userpool/{pool}"

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_dict(data)
