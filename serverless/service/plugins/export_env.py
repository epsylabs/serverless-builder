from serverless.service.plugins.generic import Generic


class ExportEnv(Generic):
    yaml_tag = "!ExportEnv"

    def __init__(self):
        super().__init__("serverless-export-env")

    def enable(self, service):
        pass