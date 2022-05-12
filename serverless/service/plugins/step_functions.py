from serverless.service.plugins.generic import Generic


class StepFunctions(Generic):
    """
    Plugin npm: https://www.npmjs.com/package/serverless-step-functions
    """

    yaml_tag = "!StepFunctionsPlugin"

    def __init__(self):
        super().__init__("serverless-step-functions")
