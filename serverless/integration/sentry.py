from serverless.service.types import Integration


class Sentry(Integration):
    def __init__(self, sentry_dsn):
        super().__init__()
        self.sentry_dsn = sentry_dsn

    def enable(self, service):
        service.provider.environment["envs"]["SENTRY_DSN"] = self.sentry_dsn
        service.provider.environment["envs"]["SENTRY_ENVIRONMENT"] = "${sls:stage}"
        service.provider.environment["envs"]["SENTRY_RELEASE"] = "${env:VERSION, ''}"
