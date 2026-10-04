from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

logger = Logger()
app = APIGatewayHttpResolver(enable_validation=True)


class HelloRequest(BaseModel):
    name: str = Field(default="world", min_length=1)


@app.get("/hello")
def get_hello() -> dict[str, str]:
    return {"message": "Hello from Lambda"}


@app.post("/hello")
def post_hello(body: HelloRequest) -> dict[str, str]:
    return {"message": f"Hello, {body.name}"}


@logger.inject_lambda_context(log_event=True)
def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """HTTP API + Function URL share payload format 2.0."""
    return app.resolve(event, context)
