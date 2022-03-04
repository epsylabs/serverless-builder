from serverless.aws.iam import IAMPreset, PolicyBuilder


class XRayService(IAMPreset):
    def __init__(self):
        super().__init__("*")

    def apply(self, policy_builder: PolicyBuilder, sid=None):
        policy_builder.allow(
            sid="Xray",
            permissions=[
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords",
                "xray:GetSamplingRules",
                "xray:GetSamplingTargets",
                "xray:GetSamplingStatisticSummaries",
            ],
            resources=["*"],
        )
