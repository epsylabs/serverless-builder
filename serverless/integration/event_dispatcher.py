from troposphere import GetAtt
from troposphere.cloudwatch import Alarm, MetricDimension

from serverless.aws.iam.event_bridge import Publish
from serverless.aws.resources.sqs import Queue
from serverless.service.types import Integration


class EventDispatcher(Integration):
    def __init__(self, event_bus) -> None:
        super().__init__()
        self.event_bus = event_bus

    def enable(self, service):
        queue = Queue(
            title="EventDispatcherDLQ",
            QueueName="event-dispatcher-dlq",
            MessageRetentionPeriod=1209600,  # 14 days in seconds
        )

        service.resources.add(queue)

        service.resources.add(
            Alarm(
                "EventDispatcherDLQCloudWatchAlarm",
                AlarmDescription="Unable to send event from handler.",
                AlarmActions=["arn:aws:sns:${aws:region}:${aws:accountId}:foxglove-${sls:stage}-cloudwatch-alerts"],
                Namespace="AWS/SQS",
                MetricName="ApproximateNumberOfMessagesVisible",
                Dimensions=[MetricDimension(Name="QueueName", Value=GetAtt("EventDispatcherDLQ", "QueueName"))],
                Statistic="Sum",
                Period=60,
                EvaluationPeriods=1,
                Threshold=1,
                ComparisonOperator="GreaterThanOrEqualToThreshold",
            )
        )
        service.provider.iam.allow(
            sid="EventDispatcherDLQBatch",
            permissions=["sqs:SendMessage", "sqs:GetQueueUrl"],
            resources=[queue.arn()],
        )

        service.provider.environment.envs["EVENTS_DLQ"] = queue.resource.QueueName
        service.provider.iam.apply(Publish(self.event_bus))


class DLQ(EventDispatcher):
    pass
