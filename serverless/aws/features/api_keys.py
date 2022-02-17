from serverless.service.types import Feature


class ApiKey:
    def __init__(self, name=None, value=None, description=None):
        if not any([name, value]):
            raise KeyError("You need to provide either name or value for key")

        self.name = name
        self.value = value
        self.description = description

    def to_dict(self):
        return {k: getattr(self, k) for k in ("name", "value", "description") if getattr(self, k)}


class ApiKeys(Feature):
    def __init__(self, keys=None, source="HEADER") -> None:
        super().__init__()
        self.keys = [k if isinstance(k, ApiKey) else ApiKey(k) for k in keys]
        self.source = source

    def enable(self, service):
        api_gw = service.provider.get("apiGateway", {})
        api_gw["apiKeySourceType"] = self.source
        api_gw["apiKeys"] = list(map(lambda x: x.to_dict(), self.keys))
