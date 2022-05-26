from serverless.service.plugins.generic import Generic


class GlobalTables(Generic):
    yaml_tag = "!DynamoTable"

    def __init__(self, regions, version="2", createStack=True):
        super().__init__("serverless-create-global-dynamodb-table")
        self.createStack = createStack
        self.regions = regions
        self.version = version

    def enable(self, service):
        super().enable(service)
        service.custom.globalTables = dict(version=self.version, regions=self.regions, createStack=self.createStack)
