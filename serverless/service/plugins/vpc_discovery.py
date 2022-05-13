from serverless.service.plugins.generic import Generic


class VpcDiscovery(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-vpc-discovery
    Example of use
    ```python
    service.plugins.add(VpcDiscovery("main", subnets=[{"tagKey": "Name", "tagValues": ["private-a", "private-b"]}]))
    ```
    """

    yaml_tag = "!VpcDiscovery"

    def __init__(self, vpc_name, subnet_names=None, subnets=None, security_group_names=None, security_groups=None):
        super().__init__("serverless-vpc-discovery")

        self.vpcName = vpc_name
        if all((subnet_names, subnets)):
            raise Exception("You can use either subnet_names or subnets.")
        if all((security_group_names, security_groups)):
            raise Exception("You can use either security_group_names or security_groups.")

        if subnet_names:
            self.subnets = [{"tagKey": "Name", "tagValues": subnet_names}]
        if subnets:
            self.subnets = subnets

        if security_group_names:
            self.subnets = [{"tagKey": "Name", "tagValues": security_group_names}]
        if security_groups:
            self.securityGroups = security_groups

    def enable(self, service):
        export = dict(self)
        export.pop("name", None)

        service.custom.vpcDiscovery = export
