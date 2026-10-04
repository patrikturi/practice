from constructs import Construct
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_lambda as lambda_

from cdk_constructs.hello_function import HelloFunction


class HelloStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello = HelloFunction(self, "Hello")

        function_url = hello.function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

        CfnOutput(
            self,
            "FunctionUrl",
            value=function_url.url,
            description="Public Function URL for the Hello Lambda",
        )

        CfnOutput(
            self,
            "FunctionName",
            value=hello.function.function_name,
            description="Lambda function name",
        )
