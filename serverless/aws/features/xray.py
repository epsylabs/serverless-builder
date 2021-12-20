from serverless.aws.iam.xray import XRayService
from serverless.service.types import Feature


class XRay(Feature):
    def __init__(self, trace_lambda=True):
        super().__init__()
        self.trace_lambda = trace_lambda

    def enable(self, service):
        service.provider.tracing = {"lambda": self.trace_lambda}
        service.provider.iam.apply(XRayService())
