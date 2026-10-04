from constructs import Construct
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk import aws_apigatewayv2_integrations as apigwv2_integrations
from aws_cdk import aws_lambda as lambda_

from cdk_constructs.hello_function import HelloFunction


class HelloStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello = HelloFunction(self, "Hello")

        function_url = hello.function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        http_api = apigwv2.HttpApi(
            self,
            "HttpApi",
            api_name="hello-http-api",
            description="Step B HTTP API for Hello Lambda",
        )
        integration = apigwv2_integrations.HttpLambdaIntegration(
            "HelloIntegration",
            hello.function,
        )
        http_api.add_routes(
            path="/hello",
            methods=[apigwv2.HttpMethod.GET, apigwv2.HttpMethod.POST],
            integration=integration,
        )

        CfnOutput(
            self,
            "FunctionUrl",
            value=function_url.url,
            description="Public Function URL (use path /hello)",
        )
        CfnOutput(
            self,
            "HttpApiUrl",
            value=f"{http_api.api_endpoint}/hello",
            description="HTTP API URL for GET/POST /hello",
        )
        CfnOutput(
            self,
            "FunctionName",
            value=hello.function.function_name,
            description="Lambda function name",
        )
