from serverless.service.plugins.generic import Generic


class Localstack(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-localstack
    """

    yaml_tag = "!LocalstackPlugin"

    def __init__(
        self,
        stages=["local"],
        host="http://localhost",
        edgePort=4566,
        autostart=True,
        networks=[],
        mountCode=False,
        sudo=False,
    ):
        super().__init__("serverless-localstack")
        self.stages = stages
        self.host = host
        self.edgePort = edgePort
        self.autostart = autostart
        self.networks = networks
        self.lambda_settings = dict(mountCode=mountCode)
        self.docker = dict(sudo=sudo)

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        export["lambda"] = export.get("lambda_settings")
        export.pop("lambda_settings", None)

        service.custom.localstack = export
        service.custom.stages = {stage: {} for stage in self.stages}
