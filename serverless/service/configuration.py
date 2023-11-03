from typing import Optional

from serverless.service.types import SmartString


class Configuration:
    def __init__(self, domain: Optional[str] = None, advanced_variables: Optional[bool] = False):
        self.domain = SmartString(domain) if domain else None
        self.advanced_variables = advanced_variables
