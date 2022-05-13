from serverless.service.plugins.generic import Generic


class IAMRoles(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-iam-roles-per-function
    """

    yaml_tag = "!IAMRolesPlugin"

    def __init__(self):
        super().__init__("serverless-iam-roles-per-function")

    def enable(self, service):
        pass
