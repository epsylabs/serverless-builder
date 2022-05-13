from serverless.service.plugins.generic import Generic


class ComposedVars(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-plugin-composed-vars
    """

    yaml_tag = "!ComposedVarsPlugin"

    def __init__(self):
        super().__init__("serverless-plugin-composed-vars")
