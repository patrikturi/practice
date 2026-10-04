#!/usr/bin/env python3
"""Fargate Spot PDF ingest: extract -> chunk -> embed (Titan V2) -> Aurora pgvector."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
import fitz  # PyMuPDF
import psycopg
from tenacity import retry, stop_after_attempt, wait_exponential

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DOCS_BUCKET = os.environ.get("DOCS_BUCKET") or os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
DOCUMENTS_TABLE = os.environ["DOCUMENTS_TABLE"]
AURORA_SECRET_ARN = os.environ["AURORA_SECRET_ARN"]
EMBED_MODEL_ID = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

CHUNK_SIZE = 1800  # ~512 tokens heuristic
CHUNK_OVERLAP = 270
EMBED_BATCH = 16

s3 = boto3.client("s3", region_name=AWS_REGION)
ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
secrets = boto3.client("secretsmanager", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def audit(event: str, **fields: Any) -> None:
    print(json.dumps({"type": "audit", "event": event, "ts": datetime.now(timezone.utc).isoformat(), **fields}))


def parse_key(key: str) -> tuple[str, str]:
    # uploads/{userId}/{documentId}/{filename}
    parts = key.split("/")
    if len(parts) < 4 or parts[0] != "uploads":
        raise ValueError(f"Unexpected S3 key layout: {key}")
    return parts[1], parts[2]


def update_status(user_id: str, document_id: str, status: str, error: str | None = None) -> None:
    table = ddb.Table(DOCUMENTS_TABLE)
    expr = "SET #s = :s, updatedAt = :u"
    names = {"#s": "status"}
    values: dict[str, Any] = {":s": status, ":u": datetime.now(timezone.utc).isoformat()}
    if error:
        expr += ", #e = :e"
        names["#e"] = "error"
        values[":e"] = error[:1000]
    table.update_item(
        Key={"userId": user_id, "documentId": document_id},
        UpdateExpression=expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )


def get_secret() -> dict[str, Any]:
    res = secrets.get_secret_value(SecretId=AURORA_SECRET_ARN)
    return json.loads(res["SecretString"])


def download_pdf(bucket: str, key: str) -> bytes:
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read()


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if text:
            pages.append((i + 1, text))
    doc.close()
    return pages


def chunk_text(pages: list[tuple[int, str]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    buffer = ""
    page_refs: list[int] = []

    def flush() -> None:
        nonlocal buffer, page_refs
        text = buffer.strip()
        if not text:
            return
        chunks.append(
            {
                "content": text,
                "metadata": {"pages": sorted(set(page_refs))},
            }
        )
        # overlap
        if len(buffer) > CHUNK_OVERLAP:
            buffer = buffer[-CHUNK_OVERLAP:]
        else:
            buffer = ""
        page_refs = page_refs[-2:] if page_refs else []

    for page_no, text in pages:
        for para in text.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            if len(buffer) + len(para) + 1 > CHUNK_SIZE:
                flush()
            buffer = f"{buffer}\n\n{para}".strip()
            page_refs.append(page_no)
            if len(buffer) >= CHUNK_SIZE:
                flush()
    flush()
    # assign indexes
    for idx, c in enumerate(chunks):
        c["chunk_index"] = idx
    return chunks


@retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(5))
def embed_batch(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for text in texts:
        body = {
            "inputText": text[:50000],
            "dimensions": 1024,
            "normalize": True,
        }
        res = bedrock.invoke_model(
            modelId=EMBED_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        payload = json.loads(res["body"].read())
        vectors.append(payload["embedding"])
    return vectors


def upsert_chunks(conn: psycopg.Connection, user_id: str, document_id: str, chunks: list[dict[str, Any]], vectors: list[list[float]]) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM document_chunks WHERE document_id = %s AND user_id = %s", (document_id, user_id))
        for chunk, vector in zip(chunks, vectors):
            cur.execute(
                """
                INSERT INTO document_chunks (id, document_id, user_id, chunk_index, content, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::vector, %s::jsonb)
                """,
                (
                    str(uuid.uuid4()),
                    document_id,
                    user_id,
                    chunk["chunk_index"],
                    chunk["content"],
                    "[" + ",".join(str(x) for x in vector) + "]",
                    json.dumps(chunk["metadata"]),
                ),
            )
    conn.commit()


def main() -> None:
    if not DOCS_BUCKET or not S3_KEY:
        raise SystemExit("S3_BUCKET/DOCS_BUCKET and S3_KEY are required")

    user_id, document_id = parse_key(S3_KEY)
    audit("ingest.start", userId=user_id, documentId=document_id, s3Key=S3_KEY)
    update_status(user_id, document_id, "processing")

    try:
        pdf_bytes = download_pdf(DOCS_BUCKET, S3_KEY)
        if len(pdf_bytes) > 100 * 1024 * 1024:
            raise ValueError("PDF exceeds 100MB limit")

        pages = extract_pages(pdf_bytes)
        chunks = chunk_text(pages)
        if not chunks:
            raise ValueError("No extractable text in PDF")

        vectors: list[list[float]] = []
        for i in range(0, len(chunks), EMBED_BATCH):
            batch = [c["content"] for c in chunks[i : i + EMBED_BATCH]]
            vectors.extend(embed_batch(batch))

        secret = get_secret()
        conninfo = (
            f"host={secret['host']} port={secret.get('port', 5432)} "
            f"dbname={secret['dbname']} user={secret['username']} "
            f"password={secret['password']} sslmode=require"
        )
        with psycopg.connect(conninfo) as conn:
            upsert_chunks(conn, user_id, document_id, chunks, vectors)

        update_status(user_id, document_id, "indexed")
        audit("ingest.complete", userId=user_id, documentId=document_id, chunks=len(chunks))
    except Exception as exc:  # noqa: BLE001
        update_status(user_id, document_id, "failed", error=str(exc))
        audit("ingest.failed", userId=user_id, documentId=document_id, error=str(exc))
        raise


if __name__ == "__main__":
    main()
