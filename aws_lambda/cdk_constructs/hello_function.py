from aws_cdk import Duration, aws_lambda as lambda_
from constructs import Construct


class HelloFunction(Construct):
    """Owns the Hello Lambda. Triggers (Function URL, API Gateway) stay in the stack."""

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.function = lambda_.Function(
            self,
            "Function",
            runtime=lambda_.Runtime.PYTHON_3_14,
            handler="handler.handler",
            code=lambda_.Code.from_asset("lambdas/hello"),
            timeout=Duration.seconds(10),
            memory_size=128,
            description="Step A hello Lambda (stdlib JSON response)",
        )
