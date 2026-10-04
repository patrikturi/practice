# Learn AWS Lambda with Python CDK (Step B)

Python 3.14 Lambda deployed with CDK, exposed via a **Function URL** and an **API Gateway HTTP API**. Runtime uses **aws-lambda-powertools** + **pydantic**, bundled with **UV**. Tooling: **UV** (Python) + **Volta** (Node for the CDK CLI).

## What you get

- `HelloFunction` construct → owns the Lambda (`python3.14` / `arm64`), bundles deps via UV
- `HelloStack` → public Function URL + HTTP API routes `GET|POST /hello`
- Handler uses Powertools `APIGatewayHttpResolver` + Pydantic body validation on `POST`

```text
curl → HTTP API /hello  ┐
                        ├→ Lambda (Powertools) → CloudWatch Logs
curl → Function URL/hello ┘
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
uv sync                              # CDK app deps
uv lock --directory lambdas/hello    # Lambda runtime lockfile (if deps change)
npm install                          # Volta uses Node 24.21.0 from package.json
```

## Deploy / invoke / destroy

```bash
npx cdk bootstrap          # once per account/region
npx cdk synth              # CloudFormation under cdk.out/ (UV local-bundles the Lambda)
npx cdk deploy             # note HttpApiUrl / FunctionUrl in the outputs

curl "<HttpApiUrl>"
curl -X POST "<HttpApiUrl>" -H 'content-type: application/json' -d '{"name":"Patrik"}'

# Function URL uses the same /hello routes:
curl "<FunctionUrl>hello"
npx cdk destroy
```

`cdk.json` runs the app with `uv run python app.py`, so CDK always uses the UV-managed 3.14 environment.

## Layout

```text
app.py                         CDK App → HelloStack
cdk.json                       app: uv run python app.py
pyproject.toml                 UV project (aws-cdk-lib, constructs)
package.json                   Volta Node 24.21.0 + aws-cdk CLI
stacks/hello_stack.py          Function URL + HTTP API + outputs
cdk_constructs/
  hello_function.py            Lambda + UV bundling
  uv_local_bundling.py         Local ILocalBundling (no Docker)
lambdas/hello/
  handler.py                   Powertools + Pydantic runtime
  pyproject.toml               aws-lambda-powertools, pydantic
  uv.lock                      locked Lambda deps
```

## Learning checkpoints

1. **Construct tree:** `App` → `HelloStack` → `HelloFunction` → `Function` → (`FunctionUrl`, `HttpApi`)
2. **Two Python projects:** root UV env runs CDK; `lambdas/hello` lockfile is what gets packaged
3. **UV bundling:** `uv export` → `uv pip install --python-platform aarch64-manylinux2014 --target …`
4. **Powertools resolver:** one handler serves HTTP API and Function URL (payload 2.0)
5. **Pydantic:** `POST /hello` validates `{"name": "..."}` via `enable_validation=True`
6. **Logs:** after one `curl`, open the function’s CloudWatch log group

## Upgrade path

### C) Richer (not implemented yet)

- DynamoDB table, env vars, IAM grants on `HelloFunction`
- Handler reads/writes the table (Powertools + Pydantic still apply)

## Next Steps
- Use CDK's PythonFunction for package build
- Add unit tests - with aws-lambda-context and aws-lambda-event fakes
- Implement Step C)
- Deploy Step A) in a closer AWS region and test latency
- Destroy all resources
