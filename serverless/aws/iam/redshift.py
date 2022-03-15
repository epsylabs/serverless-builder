from serverless.aws.iam import IAMPreset, PolicyBuilder
from serverless.service import Identifier


class RedshiftConnect(IAMPreset):
    def __init__(self, cluster, db_name, db_user):
        self.cluster = cluster
        self.db_name = db_name
        self.db_user = db_user

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            permissions=["redshift:GetClusterCredentials"],
            resources=[
                "arn:aws:redshift:${aws:region}:${aws:accountId}:cluster:" + self.cluster,
                "arn:aws:redshift:${aws:region}:${aws:accountId}:dbname:" + f"{self.cluster}/{self.db_name}",
                "arn:aws:redshift:${aws:region}:${aws:accountId}:dbuser:" + f"{self.cluster}/{self.db_user}",
            ],
            sid=sid or "RedshiftConnection" + Identifier(self.cluster).pascal,
        )


class RedshiftQuery(RedshiftConnect):
    def apply(self, policy_builder: PolicyBuilder, sid=None):
        super().apply(policy_builder, sid)
        policy_builder.allow(
            permissions=[
                "redshift-data:DescribeTable",
                "redshift-data:ExecuteStatement",
                "redshift-data:BatchExecuteStatement",
                "redshift-data:DescribeStatement",
                "redshift-data:GetStatementResult",
            ],
            resources=["*"],
            sid=sid or "RedshiftQuery" + Identifier(self.cluster).pascal,
        )
