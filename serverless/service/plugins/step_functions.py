from serverless.service.plugins.generic import Generic


class StepFunctions(Generic):
    yaml_tag = "!StepFunctionsPlugin"

    def __init__(self):
        super().__init__("serverless-step-functions")
