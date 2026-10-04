import json
from typing import Any, Protocol


class LambdaContext(Protocol):
    """Structural type for the AWS Lambda context object (stdlib-only)."""

    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: Any
    client_context: Any

    def get_remaining_time_in_millis(self) -> int: ...


def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    """HTTP-proxy response shape works for Function URL and future API Gateway."""
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"event": event, "context": {
            "function_name": context.function_name,
            "function_version": context.function_version,
            "invoked_function_arn": context.invoked_function_arn,
            "memory_limit_in_mb": context.memory_limit_in_mb,
            "aws_request_id": context.aws_request_id,
            "log_group_name": context.log_group_name,
            "log_stream_name": context.log_stream_name,
            "client_context": context.client_context,
            "remaining_time_in_millis": context.get_remaining_time_in_millis(),
        }}),
    }
