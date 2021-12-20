from serverless.service.plugins.generic import Generic


class ComposedVars(Generic):

    yaml_tag = u"!ComposedVarsPlugin"

    def __init__(self):
        super().__init__("serverless-plugin-composed-vars")
