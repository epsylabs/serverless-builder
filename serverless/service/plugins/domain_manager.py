from serverless.service.plugins.generic import Generic


class DomainManager(Generic):
    """
    Plugin homepage: https://github.com/amplify-education/serverless-domain-manager
    """
    yaml_tag = u"!DomainManagerPlugin"

    def __init__(self, domain, api="rest", stage="${sls:stage}", basePath=None, createRoute53Record=False):
        super().__init__("serverless-domain-manager")
        self[api] = dict(domain=domain, stag=stage, basePath=basePath, createRoute53Record=createRoute53Record)

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        service.custom.customDomain = export
