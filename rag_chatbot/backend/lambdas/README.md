# Backend Lambdas (TypeScript)

Node.js 20 Lambda functions written in TypeScript and bundled with esbuild.

## Layout

```
src/
  shared/          # HTTP helpers, audit logging, shared types
  chat/
  upload/
  history/
  connect/
  disconnect/
dist/<fn>/handler.js   # build output consumed by Terraform
```

## Commands

```bash
cd backend/lambdas
npm install
npm run typecheck
npm run build
```

`npm run build` emits minified CommonJS bundles under `dist/<function>/handler.js` (handler export: `handler.handler`).

Externals:

- `@aws-sdk/*` — provided by the Node.js 20 Lambda runtime
- `pg` (chat only) — provided by the PostgreSQL Lambda layer

Re-run `npm run build` before `terraform apply` so archives pick up the latest `dist/` output.
