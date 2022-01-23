from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class SQSEvent(YamlOrderedDict):
    yaml_tag = "sqs"

    def __init__(self, arn, batchSize=10, maximumBatchingWindow=10, enabled=True, filterPatterns=None):
        super().__init__()
        self.arn = arn
        self.batchSize = batchSize
        self.maximumBatchingWindow = maximumBatchingWindow
        self.enabled = enabled
        if filterPatterns:
            self.filterPatterns = filterPatterns


class SQSFunction(Function):
    yaml_tag = "!SQSFunction"

    def __init__(
        self,
        service,
        name,
        description,
        arn,
        batchSize=10,
        maximumBatchingWindow=10,
        enabled=True,
        filterPatterns=None,
        handler=None,
        timeout=None,
        layers=None,
        **kwargs
    ):
        super().__init__(service, name, description, handler, timeout, layers, **kwargs)
        self.trigger(SQSEvent(arn, batchSize, maximumBatchingWindow, enabled, filterPatterns))
