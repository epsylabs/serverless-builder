from serverless.service.plugins.generic import Generic


class StepFunctions(Generic):

    yaml_tag = u"!StepFunctionsPlugin"

    def __init__(self):
        super().__init__("serverless-step-functions")
