from serverless.service.plugins.generic import Generic


class VpcDiscovery(Generic):
    """
    Plugin homepage: https://www.npmjs.com/package/serverless-vpc-discovery
    Example of use
    ```python
    service.plugins.add(VpcDiscovery("main", [{"tagKey": "Name", "tagValues": ["private-a", "private-b"]}]))
    ```
    """
    yaml_tag = u"!VpcDiscovery"

    def __init__(self, vpc_name, subnets=None, security_groups=None):
        super().__init__("serverless-vpc-discovery")

        self.vpc_name = vpc_name
        if subnets:
            self.subnets = subnets
        if security_groups:
            self.security_groups = security_groups

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        service.custom.vpcDiscovery = export
