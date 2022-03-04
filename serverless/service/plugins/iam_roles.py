from serverless.service.plugins.generic import Generic


class IAMRoles(Generic):
    yaml_tag = "!IAMRolesPlugin"

    def __init__(self, hooks=None, inject_to_package=None):
        super().__init__("serverless-iam-roles-per-function")

    def enable(self, service):
        pass
