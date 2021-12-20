from troposphere.sqs import Queue

from serverless.service.types import Identifier, YamlOrderedDict


class Function(YamlOrderedDict):
    yaml_tag = "!Function"

    def __init__(self, service, name, description, handler=None, timeout=None, layers=None):
        super().__init__()
        self.service = service
        self.name = Identifier(name)
        self.description = description

        if not handler:
            handler = f"{self.service.service.snake}/{self.name.snake}:handler"

        self.handler = handler
        self.events = []

        if layers:
            self.layers = layers

        if timeout:
            self.timeout = timeout

    def trigger(self, event):
        self.events.append(event)

    def use_async_dlq(self, dlqArn=None, maximumEventAge=3600, maximumRetryAttempts=3):
        if not dlqArn:
            queue = Queue(QueueName=f"{self.name.spinal}-dlq", title=f"{self.name.pascal}DLQ")
            self.service.resources.add(queue)
            dlqArn = queue.get_att("Arn").to_dict()

        self.destinations = dict(onFailure=dlqArn)

        if maximumRetryAttempts:
            self.maximumRetryAttempts = maximumRetryAttempts

        if maximumEventAge:
            self.maximumEventAge = maximumEventAge

        return self

    @classmethod
    def to_yaml(cls, dumper, data):
        events = data.events
        data.pop("service", None)

        data.events = [{event.yaml_tag: event} for event in events]

        return dumper.represent_dict(data)
