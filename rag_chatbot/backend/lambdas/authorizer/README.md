# Authorizer

HTTP API authorization uses API Gateway’s built-in **JWT authorizer** against Cognito (see `terraform/modules/api`).

WebSocket `$connect` validates JWTs in `src/connect/handler.ts` via JWKS (`jose`).

A separate Lambda authorizer is not required for v1.
