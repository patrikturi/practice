# Security Implementation

This system is designed around least privilege, encryption everywhere, authenticated APIs, abuse controls, and auditable access.

## Controls matrix

| Requirement | Implementation |
| --- | --- |
| Encryption in transit | TLS 1.2+ on CloudFront, API Gateway, Aurora (`sslmode=require`), VPC endpoint HTTPS |
| Encryption at rest | S3 SSE-KMS (CMK) for documents; Aurora storage encryption (KMS); DynamoDB SSE; CloudWatch/CloudTrail encrypted storage |
| User authentication | Amazon Cognito User Pool; SPA PKCE/code flow; JWT on HTTP API; JWT verified on WebSocket `$connect` |
| Session management | Cognito access/refresh tokens; WS connection records TTL in DynamoDB |
| Least-privilege IAM | Separate roles per Lambda and ECS task; Bedrock limited to Claude Sonnet 5.5 + Titan Embed V2; S3 limited to `uploads/*` |
| Rate limiting | AWS WAF rate-based rule (per IP); API Gateway stage throttles; app-level message length checks |
| Audit logging | CloudTrail (management events); structured JSON app audits (`type=audit`) in Lambda/ECS logs; API access logs |
| Document isolation | Objects under `uploads/{userId}/...`; DynamoDB/Aurora queries scoped by Cognito `sub` |

## Identity and access

### Cognito

- Password policy: 12+ chars with upper/lower/number/symbol
- Email verification required
- Token revocation enabled
- SPA client has **no** client secret

### API authorization

- HTTP API: JWT authorizer validates Cognito issuer + audience
- WebSocket: `$connect` Lambda verifies JWT via JWKS (`jose`), stores `connectionId → userId`
- Chat path resolves identity from `WsConnections`, not from untrusted body fields

### IAM highlights

| Principal | Allowed |
| --- | --- |
| `upload` Lambda | `s3:PutObject` on `uploads/*`, KMS generate/encrypt, DynamoDB documents |
| `chat` Lambda | Bedrock invoke/stream, Secrets Manager Aurora secret, SSM WS endpoint param, DynamoDB chat/cache/WS, `execute-api:ManageConnections` |
| `pdf_ingest` task | `s3:GetObject` uploads, KMS decrypt, DynamoDB document status, Secrets Manager, Bedrock embed only |
| Step Functions | `ecs:RunTask` on ingest task definition, pass ECS roles, DLQ send |

No wildcard `s3:*` or `bedrock:*` on all resources.

## Data protection

### Documents (S3)

- Default encryption: SSE-KMS with customer-managed key (`enable_key_rotation = true`)
- Bucket owner enforced via public access block
- Bucket policy **Deny** on `aws:SecureTransport=false`
- Presigned PUT URLs expire in 15 minutes
- Max upload size enforced in API (`104857600` bytes)

### Vectors & chat

- Aurora in private subnets; SG allows 5432 only from Lambda + Fargate SGs
- Credentials in Secrets Manager (not env plaintext beyond runtime fetch)
- Chat history and cache encrypted at rest by DynamoDB

## Network security

- Private subnets for Aurora, Fargate ingest, VPC-attached chat Lambda
- Interface endpoints for Bedrock Runtime and Secrets Manager
- Gateway endpoints for S3 and DynamoDB
- CloudFront security response headers (HSTS, XSS, frame deny, nosniff)

## Abuse prevention

1. **WAF** regional Web ACL with rate-based rule + AWS Managed Common Rule Set (associated to HTTP stage)
2. **API Gateway** throttling: burst 200 / rate 100 (stage defaults)
3. **App limits**: reject chat messages > 8k chars; PDF-only uploads
4. **Optional hardening** (not enabled by default): ClamAV scanning Lambda on `ObjectCreated` before Step Functions start

## Audit & monitoring

| Signal | Destination |
| --- | --- |
| AWS API activity | CloudTrail → logs bucket |
| HTTP access | API Gateway access logs (includes JWT `sub` when present) |
| App events | `audit` JSON logs: `document.upload_created`, `ingest.*`, `chat.complete`, `ws.connect` |
| Alarms | Chat Lambda errors, chat p95 duration, CloudWatch dashboard for Lambda + Aurora ACU |

Retain CloudWatch log groups for 30 days (adjust for compliance).

## Compliance posture notes

- Suitable starting point for internal/knowledge-base chatbots
- For regulated workloads, add: AWS Config rules, PrivateLink-only admin access, CMK grants review, retention policies, DLP on prompts/outputs, and formal threat modeling
- Do not log raw document contents or full prompts in production audit sinks if data classification forbids it—trim to IDs, hashes, and latency fields

## Incident response quick actions

1. Disable Cognito app client / lock user pool
2. Block offending IPs in WAF
3. Set chat Lambda reserved concurrency to `0` to shed load
4. Revoke suspicious refresh tokens; rotate Aurora secret
5. Preserve CloudTrail and log groups before remediation changes
