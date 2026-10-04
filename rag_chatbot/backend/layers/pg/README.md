# PostgreSQL Lambda layer

Before `terraform apply`, install dependencies:

```bash
cd backend/layers/pg/nodejs
npm install --omit=dev
```

The Terraform `archive_file` packages this directory as a Lambda layer compatible with `nodejs20.x`.
