from serverless.service.plugins.generic import Generic


class LambdaDLQ(Generic):
    yaml_tag = "!LambdaDLQ"

    def __init__(self):
        super().__init__("serverless-plugin-lambda-dead-letter")

    def enable(self, service):
        pass
