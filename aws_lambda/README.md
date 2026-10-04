# Learn AWS Lambda with Python CDK (Step A)

Minimal Python 3.14 Lambda deployed with CDK, exposed via a **Function URL**. Tooling: **UV** (Python) + **Volta** (Node for the CDK CLI).

## What you get

- `HelloFunction` construct → owns the Lambda (`python3.14`)
- `HelloStack` → adds a public Function URL (`AuthType: NONE`) and prints the URL
- Handler returns HTTP-proxy JSON: `{"message": "Hello from Lambda"}`

```text
curl → Function URL → Lambda → CloudWatch Logs
```

## Prerequisites

- [UV](https://docs.astral.sh/uv/)
- [Volta](https://volta.sh/) (Node pinned to **24.21.0** in `package.json`)
- AWS credentials configured (`aws sts get-caller-identity` works)
- One-time CDK bootstrap in your account/region

## Setup

```bash
cd aws_lambda
uv python install 3.14
uv sync
npm install   # Volta uses Node 24.21.0 from package.json
```

## Deploy / invoke / destroy

```bash
npx cdk bootstrap          # once per account/region
npx cdk synth              # CloudFormation under cdk.out/
npx cdk deploy             # note FunctionUrl in the outputs
curl "<FunctionUrl>"
npx cdk destroy
```

`cdk.json` runs the app with `uv run python app.py`, so CDK always uses the UV-managed 3.14 environment.

## Layout

```text
app.py                      CDK App → HelloStack
cdk.json                    app: uv run python app.py
pyproject.toml              UV project (aws-cdk-lib, constructs)
package.json                Volta Node 24.21.0 + aws-cdk CLI
stacks/hello_stack.py       Function URL + outputs
cdk_constructs/             HelloFunction (named to avoid shadowing PyPI `constructs`)
lambdas/hello/handler.py    Runtime code (stdlib only)
```

## Learning checkpoints

1. **Construct tree:** `App` → `HelloStack` → `HelloFunction` → `Function` → `FunctionUrl`
2. **UV vs Lambda:** UV runs CDK locally; Lambda runs `handler.py` on AWS with `python3.14`
3. **Volta’s job:** pins Node for the CDK CLI only—not the Lambda runtime
4. **Synth vs deploy:** inspect `cdk.out/`, then deploy real resources
5. **Logs:** after one `curl`, open the function’s CloudWatch log group

## Upgrade path (not implemented yet)

### B) Practical API + real Lambda deps

- Add API Gateway **HTTP API** (`GET /hello`, optional `POST`) via `HttpLambdaIntegration`
- Add **aws-lambda-powertools** and **pydantic** to the Lambda asset
- Bundle deps with UV (packaging lesson deferred from A)

### C) Richer

- DynamoDB table, env vars, IAM grants on `HelloFunction`
- Handler reads/writes the table (Powertools + Pydantic still apply)

The handler already uses the HTTP-proxy response shape so Function URL (A) and API Gateway (B) stay compatible.
