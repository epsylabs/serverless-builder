from troposphere.sqs import Queue

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

        # if retryPolicy:
        self.retryPolicy = retryPolicy


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
        **kwargs,
    ):
        super().__init__(service, name, description, handler, timeout, layers, **kwargs)
        self.trigger(EventBridgeEvent(eventBus, pattern, deadLetterQueueArn, retryPolicy))

    def use_delivery_dlq(self, dlqArn=None, retryPolicy=None):
        if not dlqArn:
            queue = Queue(QueueName=f"{self.name.spinal}-delivery-dlq", title=f"{self.name.pascal}DeliveryDLQ")
            self._service.resources.add(queue)
            dlqArn = queue.get_att("Arn").to_dict()

        for event in self.events:
            event.deadLetterQueueArn = dlqArn
            if retryPolicy:
                event.retryPolicy = retryPolicy

        return self
