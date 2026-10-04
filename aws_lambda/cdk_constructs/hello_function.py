from pathlib import Path

from aws_cdk import AssetHashType, BundlingOptions, Duration, aws_lambda as lambda_
from constructs import Construct

from cdk_constructs.uv_local_bundling import UvLocalBundling

_HELLO_SOURCE = Path(__file__).resolve().parents[1] / "lambdas" / "hello"


class HelloFunction(Construct):
    """Owns the Hello Lambda. Triggers (Function URL, API Gateway) stay in the stack."""

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        architecture = lambda_.Architecture.ARM_64

        self.function = lambda_.Function(
            self,
            "Function",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=architecture,
            handler="handler.handler",
            code=lambda_.Code.from_asset(
                str(_HELLO_SOURCE),
                exclude=[".venv", "**/__pycache__", "**/*.pyc"],
                # Hash the bundled output so bundler/platform fixes invalidate the asset.
                asset_hash_type=AssetHashType.OUTPUT,
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_14.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "echo 'UV local bundling failed' && exit 1",
                    ],
                    local=UvLocalBundling(_HELLO_SOURCE, architecture),
                ),
            ),
            timeout=Duration.seconds(10),
            memory_size=128,
            description="Step B hello Lambda (Powertools + Pydantic)",
        )
