from serverless.service.plugins.generic import Generic
import troposphere.ssm as ssm


class DomainManager(Generic):
    """
    Plugin npm: https://github.com/amplify-education/serverless-domain-manager
    """

    yaml_tag = "!DomainManagerPlugin"

    def __init__(self, domain="api", api="rest", stage="${sls:stage}", base_path="", create_route_53_record=False, **kwargs):
        super().__init__("serverless-domain-manager")

        kwargs.setdefault("domainName", f"{api}.{domain}")
        self[api] = dict(
            stage=stage, basePath=base_path, createRoute53Record=create_route_53_record, **kwargs
        )

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        service.custom.customDomain = export
        param = service.resources.parameter(
            "RESTApiId",
            "api-id",
            {"Fn::GetAtt": ["ApiGatewayRestApi", "RootResourceId"]}
        )
