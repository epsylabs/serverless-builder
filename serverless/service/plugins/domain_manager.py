from serverless.service.plugins.generic import Generic


class DomainManager(Generic):
    """
    Plugin homepage: https://github.com/amplify-education/serverless-domain-manager
    """

    yaml_tag = "!DomainManagerPlugin"

    def __init__(self, domain, api="rest", stage="${sls:stage}", base_path=None, create_route_53_record=False):
        super().__init__("serverless-domain-manager")
        self[api] = dict(
            domainName=f"{api}.{domain}", stage=stage, basePath=base_path, createRoute53Record=create_route_53_record
        )

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        service.custom.customDomain = export
