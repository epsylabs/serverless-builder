from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class KinesisReader(IAMPreset):
    def __init__(self, stream):
        if not stream.startswith("arn:aws"):
            stream = "arn:aws:kinesis:${aws:region}:${aws:accountId}:stream/" + stream

        self.stream = stream

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "kinesis:DescribeStream",
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:ListShards",
                "kinesis:ListStreams",
            ],
            resources=[self.stream],
            sid=sid or "KinesisStreamReader" + Identifier(self.stream, safe=True).pascal,
        )


class KinesisWriter(IAMPreset):
    def __init__(self, stream):
        if not stream.startswith("arn:aws"):
            stream = "arn:aws:kinesis:${aws:region}:${aws:accountId}:stream/" + stream

        self.stream = stream

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=[
                "kinesis:DescribeStream",
                "kinesis:PutRecord",
                "kinesis:PutRecords",
            ],
            resources=[self.stream],
            sid=sid or "KinesisStreamWriter" + Identifier(self.stream, safe=True).pascal,
        )
