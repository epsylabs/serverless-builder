from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class KinesisEvent(YamlOrderedDict):
    yaml_tag = "stream"

    def __init__(
        self,
        arn,
        batchSize=10,
        maximumRecordAgeInSeconds=120,
        startingPosition="LATEST",
        functionResponseType="ReportBatchItemFailures",
    ):
        super().__init__()
        self.arn = arn
        self.batchSize = batchSize
        self.maximumRecordAgeInSeconds = maximumRecordAgeInSeconds
        self.startingPosition = startingPosition
        self.functionResponseType = functionResponseType


class KinesisFunction(Function):
    yaml_tag = "!KinesisFunction"

    def __init__(
        self,
        stream,
        service,
        name,
        description,
        handler=None,
        timeout=None,
        layers=None,
        batch_size=10,
        maximum_record_age_in_seconds=120,
        starting_position="LATEST",
        function_response_type="ReportBatchItemFailures",
        **kwargs,
    ):
        super().__init__(service, name, description, handler, timeout, layers, **kwargs)
        self.trigger(
            KinesisEvent(
                arn=stream,
                batchSize=batch_size,
                maximumRecordAgeInSeconds=maximum_record_age_in_seconds,
                startingPosition=starting_position,
                functionResponseType=function_response_type,
            )
        )
