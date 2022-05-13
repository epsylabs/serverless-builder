from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class RetryPolicy(YamlOrderedDict):
    yaml_tag = "RetryPolicy"

    def __init__(self, maximumRetryAttempts=2, maximumEventAge=3600):
        super().__init__()
        self.maximumEventAge = maximumEventAge
        self.maximumRetryAttempts = maximumRetryAttempts


class EventBridgeEvent(YamlOrderedDict):
    yaml_tag = "eventBridge"

    def __init__(self, eventBus, pattern=None, deadLetterQueueArn=None, retryPolicy=None):
        super().__init__()
        self.eventBus = eventBus
        self.pattern = pattern

        if deadLetterQueueArn:
            self.deadLetterQueueArn = deadLetterQueueArn

        if retryPolicy:
            self.retryPolicy = retryPolicy.copy()


class EventBridgeFunction(Function):
    yaml_tag = "!EventBridgeFunction"

    def __init__(
        self,
        service,
        name,
        description,
        eventBus,
        pattern=None,
        deadLetterQueueArn=None,
        retryPolicy=None,
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
        self.trigger(EventBridgeEvent(eventBus, pattern, deadLetterQueueArn, retryPolicy))
