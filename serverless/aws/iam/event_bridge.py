from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class Publish(IAMPreset):
    def __init__(self, event_bus):
        if not event_bus.startswith("arn:aws"):
            event_bus = "arn:aws:events:${aws:region}:${aws:accountId}:event-bus/" + event_bus

        self.event_bus = event_bus

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=["events:PutEvents"],
            resources=[self.event_bus],
            sid=sid or "EventBridgePublisher" + Identifier(self.event_bus, safe=True).pascal.replace("_", ""),
        )
