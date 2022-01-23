from serverless.aws.iam import IAMPreset


class XRayService(IAMPreset):
    def __init__(self):
        super().__init__("*")

    def apply(self, service):
        service.provider.iam.allow(
            "Xray",
            [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords",
                "xray:GetSamplingRules",
                "xray:GetSamplingTargets",
                "xray:GetSamplingStatisticSummaries",
            ],
            ["*"],
        )
