import json
from typing import Any


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """HTTP-proxy response shape works for Function URL and future API Gateway."""
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"message": "Hello from Lambda"}),
    }
