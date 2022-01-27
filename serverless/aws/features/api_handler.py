from troposphere import Ref
from troposphere.apigateway import GatewayResponse

from serverless.service.types import Feature


class DefaultFourHundredResponse(Feature):
    def enable(self, service):
        service.resources.add(
            GatewayResponse(
                "GatewayResponseDefault4XX",
                ResponseParameters={
                    "gatewayresponse.header.Access-Control-Allow-Origin": "'*'",
                    "gatewayresponse.header.Access-Control-Allow-Headers": "'*'",
                },
                ResponseType="DEFAULT_4XX",
                RestApiId=Ref("ApiGatewayRestApi"),
            )
        )
