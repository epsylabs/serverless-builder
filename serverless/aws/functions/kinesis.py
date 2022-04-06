from serverless.aws.functions.generic import Function
from serverless.service.types import YamlOrderedDict


class KinesisEvent(YamlOrderedDict):
    yaml_tag = "stream"

    def __init__(
        self,
        arn,
        batchSize=10,
        maximumRecordAgeInSeconds=120,
        maximumRetryAttempts=5,
        startingPosition="LATEST",
        functionResponseType="ReportBatchItemFailures",
        destinations=None,
    ):
        super().__init__()
        self.arn = arn
        self.batchSize = batchSize
        self.maximumRecordAgeInSeconds = maximumRecordAgeInSeconds
        self.maximumRetryAttempts = maximumRetryAttempts
        self.startingPosition = startingPosition
        self.functionResponseType = functionResponseType

        if destinations:
            self.destinations = destinations


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
        maximum_retry_attempts=5,
        starting_position="LATEST",
        function_response_type="ReportBatchItemFailures",
        destinations=None,
        use_dlq=True,
        use_async_dlq=True,
        **kwargs,
    ):
        super().__init__(
            service, name, description, handler, timeout, layers, use_dlq=use_dlq, use_async_dlq=use_async_dlq, **kwargs
        )
        self.trigger(
            KinesisEvent(
                arn=stream,
                batchSize=batch_size,
                maximumRecordAgeInSeconds=maximum_record_age_in_seconds,
                maximumRetryAttempts=maximum_retry_attempts,
                startingPosition=starting_position,
                functionResponseType=function_response_type,
                destinations=destinations,
            )
        )
