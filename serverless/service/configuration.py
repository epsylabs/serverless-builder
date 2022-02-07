from serverless.service.types import SmartString


class Configuration:
    def __init__(self, domain=None):
        self.domain = SmartString(domain) if domain else None
