# Deployment Guide

Step-by-step deployment for the AWS Claude RAG Chatbot (`us-east-1` by default).

## Prerequisites

- AWS account with admin (or equivalent) permissions
- AWS CLI v2 configured (`aws configure`)
- Terraform >= 1.5
- Node.js 20+
- Docker (for PDF ingest image)
- Git

## 1. Enable Bedrock model access

In the Amazon Bedrock console (region `us-east-1`):

1. Open **Model access** / marketplace entitlements for Anthropic and Amazon models.
2. Enable:
   - **Claude Sonnet 5.5** (use inference profile `global.anthropic.claude-sonnet-5-5`)
   - **Amazon Titan Text Embeddings V2** (`amazon.titan-embed-text-v2:0`)
3. Wait until status is **Access granted**.

Verify:

```bash
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId, 'claude-sonnet-5-5') || contains(modelId, 'titan-embed-text-v2')].modelId"
```

## 2. Build TypeScript Lambdas + layer

```bash
# PostgreSQL layer (used by chat for pg native client)
cd backend/layers/pg/nodejs && npm install --omit=dev && cd -

# Compile/bundle Lambdas → backend/lambdas/dist/<fn>/handler.js
cd backend/lambdas
npm install
npm run typecheck
npm run build
cd ../..
```

Terraform packages the **`dist/`** bundles (not the TypeScript sources). Re-run `npm run build` after any Lambda code change before `terraform apply`.

## 3. Configure Terraform

```bash
cd terraform/environments/dev
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

- Set a **globally unique** `cognito_domain_prefix`
- Keep localhost callback URLs for first apply
- Optionally configure remote state backend in `main.tf`

```bash
terraform init
terraform plan
terraform apply
```

Capture outputs:

```bash
terraform output
```

You will need:

- `http_api_endpoint`
- `websocket_api_endpoint`
- `website_url` / `frontend_bucket_id` / `cloudfront_distribution_id`
- `cognito_user_pool_id` / `cognito_client_id`
- `ecr_repository_url`
- `aurora_endpoint` / `aurora_secret_arn`
- `docs_bucket_id`

## 4. Bootstrap Aurora schema (pgvector)

Retrieve credentials and run [`modules/data/schema.sql`](../terraform/modules/data/schema.sql).

Option A — from a bastion / VPN / SSM port-forward into the VPC:

```bash
SECRET_ARN=$(terraform output -raw aurora_secret_arn)
aws secretsmanager get-secret-value --secret-id "$SECRET_ARN" --query SecretString --output text > /tmp/aurora.json

# Connect with psql using host/user/password/dbname from /tmp/aurora.json
psql "host=... dbname=ragchat user=ragadmin sslmode=require" \
  -f ../../modules/data/schema.sql
```

Option B — one-off ECS/Fargate exec task with `psql` in the private subnets (same security group path as ingest).

Confirm:

```sql
\dx
\d document_chunks
```

## 5. Build and push PDF ingest image

```bash
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR=$(terraform output -raw ecr_repository_url)

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t ragchat-pdf-ingest ../../../../backend/workers/pdf_ingest
docker tag ragchat-pdf-ingest:latest "$ECR:latest"
docker push "$ECR:latest"
```

## 6. Update Cognito / CORS with CloudFront URL

```bash
WEB=$(terraform output -raw website_url)
```

Update `terraform.tfvars` callback/logout/CORS entries to include `$WEB`, then:

```bash
terraform apply
```

## 7. Configure and deploy frontend

```bash
cd ../../../../frontend
cp .env.example .env
```

Fill `.env` from Terraform outputs:

```env
VITE_AWS_REGION=us-east-1
VITE_COGNITO_USER_POOL_ID=...
VITE_COGNITO_CLIENT_ID=...
VITE_HTTP_API_URL=https://....execute-api.us-east-1.amazonaws.com/prod
VITE_WS_API_URL=wss://....execute-api.us-east-1.amazonaws.com/prod
```

Build and publish:

```bash
npm install
npm run build

BUCKET=$(cd ../terraform/environments/dev && terraform output -raw frontend_bucket_id)
DIST=$(cd ../terraform/environments/dev && terraform output -raw cloudfront_distribution_id)

aws s3 sync dist/ "s3://$BUCKET/" --delete
aws cloudfront create-invalidation --distribution-id "$DIST" --paths "/*"
```

Open `website_url`.

## 8. Smoke tests

1. **Auth**: Sign up → confirm email → sign in.
2. **Upload**: Upload a small PDF (<5MB). Status should move `pending` → `processing` → `indexed` (watch DynamoDB or UI).
3. **Chat**: Ask a question answered only by that PDF. Expect streamed tokens and citation snippets.
4. **Cache**: Repeat the same question; response should include `cached`.
5. **History**: Refresh; prior session appears in sidebar.

CLI checks:

```bash
aws logs tail /aws/lambda/ragchat-dev-chat --follow
aws logs tail /ecs/ragchat-dev-pdf-ingest --follow
```

## 9. Local frontend development

```bash
cd frontend
npm run dev
```

Ensure Cognito callback URLs include `http://localhost:5173/callback` and CORS allows that origin.

## 10. Tear down (dev)

```bash
cd terraform/environments/dev
terraform destroy
```

Empty S3 buckets first if destroy fails on non-empty buckets:

```bash
aws s3 rm "s3://$(terraform output -raw docs_bucket_id)" --recursive
aws s3 rm "s3://$(terraform output -raw frontend_bucket_id)" --recursive
```

## Operational notes

- Chat SLA targets **time-to-first-token < 2s** for typical / cached queries; full completions may take longer.
- Large PDFs (up to 100MB) ingest asynchronously on **Fargate Spot**; chat remains available during indexing.
- If Spot capacity is unavailable, Step Functions retries; failures land in the ingest DLQ.
- After first apply, confirm SSM parameter `/{name_prefix}/websocket-management-endpoint` exists (used by chat Lambda for `ManageConnections`).
