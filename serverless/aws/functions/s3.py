from serverless.aws.functions.generic import Function
from serverless.service import YamlOrderedDict


class S3Event(YamlOrderedDict):
    yaml_tag = "s3"

    def __init__(self, bucket, event, rules=None):
        super().__init__()
        self.bucket = bucket
        self.event = event

        if rules:
            self.rules = rules


class S3Function(Function):
    yaml_tag = "!S3Function"

    def __init__(
        self,
        service,
        name,
        description,
        bucket,
        event,
        rules=None,
        handler=None,
        timeout=None,
        layers=None,
        use_dlq=True,
        use_async_dlq=True,
        **kwargs,
    ):
        super().__init__(
            service, name, description, handler, timeout, layers, use_dlq=use_dlq, use_async_dlq=use_async_dlq, **kwargs
        )
        self.trigger(S3Event(bucket, event, rules))
