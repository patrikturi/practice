# Cost Estimation

Target: **under $200/month** for moderate usage in `us-east-1`.

## Usage assumptions (moderate)

| Metric | Value |
| --- | --- |
| Chat turns | ~10,000 / month |
| Avg input tokens / turn (prompt + context) | ~2,500 |
| Avg output tokens / turn | ~400 |
| Semantic + prompt cache hit rate | ~35% |
| PDF ingest jobs | ~50 / month |
| Avg PDF size | 10 MB (peak supported 100 MB) |
| Concurrent users (peak) | 100 |
| Indexed documents | 1,000+ |

## Monthly estimate by service

| Service | Estimate (USD) | Notes |
| --- | --- | --- |
| Amazon Bedrock — Claude Sonnet 5.5 | $50–80 | Dominant variable; caching required to stay in band |
| Amazon Bedrock — Titan Embeddings V2 | $2–8 | Query + ingest embeddings (~$0.02 / 1M tokens) |
| Aurora PostgreSQL Serverless v2 + pgvector | $45–70 | `min_capacity=0`, `max_capacity=4`; scales with query load |
| AWS Lambda | $5–12 | Chat reserved concurrency 50; short connect/upload/history |
| API Gateway (HTTP + WebSocket) | $5–10 | Messages + connection-minutes |
| DynamoDB (on-demand) | $5–10 | Sessions, messages, docs, cache, connections |
| ECS Fargate Spot (ingest) | $5–15 | 2 vCPU / 4 GB tasks; Spot discount |
| S3 (docs + logs + frontend) | $3–8 | KMS-encrypted docs; versioning |
| CloudFront | $2–6 | SPA + TLS |
| Cognito | $0–5 | Free tier covers many MAUs |
| NAT Gateway | $10–20 | Optional cost lever: reduce via more VPC endpoints / single NAT |
| WAF + CloudWatch + CloudTrail | $10–20 | Rate limits, alarms, audit trail |
| **Total** | **~$130–200** | Bedrock + Aurora + NAT are the main swings |

## Why not OpenSearch Serverless?

Classic OpenSearch Serverless VECTORSEARCH often carries an idle floor near **~$700/month**. That alone breaks the $200 target. Aurora Serverless v2 + `pgvector` is the cost-fit equivalent for 1000+ documents and moderate QPS.

## Cost controls built into the design

1. **Semantic cache** (DynamoDB TTL 1h) avoids repeat Claude calls for identical user queries.
2. **Bedrock prompt caching** (where available for the model) reduces input token cost on stable system/context prefixes.
3. **Fargate Spot** for PDF ingest (non-latency-critical path).
4. **Aurora scale-to-zero** (`min_capacity = 0`) when idle.
5. **VPC gateway/interface endpoints** for S3, DynamoDB, Bedrock Runtime, Secrets Manager to shrink NAT data processing.
6. **Pay-per-request** DynamoDB and Lambda; no always-on app servers.
7. **CloudFront PriceClass_100** for static assets.

## Scaling levers if spend rises

| Lever | Effect |
| --- | --- |
| Increase cache TTL / normalize queries more aggressively | Lower Bedrock chat spend |
| Lower `maxTokens` / tighten retrieval `top_k` | Fewer output/input tokens |
| Disable NAT (`enable_nat_gateway=false`) once ECR/pull paths are endpoint-covered | Save ~$30+/mo (advanced) |
| Lower Aurora `max_capacity` if ACU alarms stay low | Cap database spend |
| Batch ingest during off-peak | Improve Spot fulfillment, less retry waste |

## Example Bedrock ballpark (illustrative)

Without cache, 10k turns × (2.5k in + 0.4k out) is the main driver. With ~35% full-answer cache hits and shorter cached responses, effective billable turns drop materially—budget **$50–80** for Claude at moderate quality settings (`temperature=0.2`, `maxTokens=2048`).

Re-validate with [AWS Pricing Calculator](https://calculator.aws/) and Bedrock cost allocation tags after two weeks of real traffic.
