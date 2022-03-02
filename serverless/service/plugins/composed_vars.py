from serverless.service.plugins.generic import Generic


class ComposedVars(Generic):
    yaml_tag = "!ComposedVarsPlugin"

    def __init__(self):
        super().__init__("serverless-plugin-composed-vars")
