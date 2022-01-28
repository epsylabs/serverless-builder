from troposphere import GetAtt
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.sqs import Queue

from serverless.service.types import Integration


class DLQ(Integration):
    def enable(self, service):
        service.resources.add(
            Queue(
                "EventDispatcherDLQ",
                QueueName="${self:service}-event-dispatcher-dlq",
                MessageRetentionPeriod=1209600,  # 14 days in seconds
            )
        )
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
            "EventDispatcherDLQBatch", "sqs:SendMessageBatch", [{"Fn::GetAtt": ["EventDispatcherDLQ", "Arn"]}]
        )
