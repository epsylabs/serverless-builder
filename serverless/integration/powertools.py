from serverless.service.types import Integration


class Powertools(Integration):
    """
    Homepage: https://awslabs.github.io/aws-lambda-powertools-python/latest/
    """

    def enable(self, service):
        service.provider.environment["envs"]["POWERTOOLS_SERVICE_NAME"] = "${self:service}"
        service.provider.environment["envs"]["POWERTOOLS_LOGGER_LOG_EVENT"] = "${self:custom.vars.log_event}"
