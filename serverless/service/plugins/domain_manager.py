from serverless.service.plugins.generic import Generic


class DomainManager(Generic):
    yaml_tag = u"!DomainManagerPlugin"

    def __init__(self, domain, api="rest", stage="${self:custom.stage}", basePath=None, createRoute53Record=False):
        super().__init__("serverless-domain-manager")
        self[api] = dict(domain=domain, stag=stage, basePath=basePath, createRoute53Record=createRoute53Record)
