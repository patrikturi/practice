import { randomUUID } from 'node:crypto';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, QueryCommand, GetCommand } from '@aws-sdk/lib-dynamodb';
import type { APIGatewayProxyHandlerV2WithJWTAuthorizer } from 'aws-lambda';
import { audit } from '../shared/audit.js';
import { getUserId, json, requireEnv, type HttpEvent } from '../shared/http.js';

const s3 = new S3Client({});
const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));

const DOCUMENTS_TABLE = requireEnv('DOCUMENTS_TABLE');
const DOCS_BUCKET = requireEnv('DOCS_BUCKET');
const MAX_UPLOAD_BYTES = process.env.MAX_UPLOAD_BYTES ?? '104857600';

export const handler: APIGatewayProxyHandlerV2WithJWTAuthorizer = async (event) => {
  const userId = getUserId(event);
  if (!userId) return json(401, { error: 'Unauthorized' });

  const method = event.requestContext.http.method;
  const path = event.rawPath || '';

  try {
    if (method === 'POST' && path.endsWith('/documents')) {
      return await createUpload(userId, event);
    }
    if (method === 'GET' && /\/documents\/[^/]+$/.test(path)) {
      const id = event.pathParameters?.id;
      if (!id) return json(400, { error: 'Missing document id' });
      return await getDocument(userId, id);
    }
    if (method === 'GET' && path.endsWith('/documents')) {
      return await listDocuments(userId);
    }
    return json(404, { error: 'Not found' });
  } catch (err) {
    console.error(err);
    audit('document.error', {
      userId,
      message: err instanceof Error ? err.message : String(err),
    });
    return json(500, { error: 'Internal error' });
  }
};

async function createUpload(userId: string, event: HttpEvent) {
  const body = JSON.parse(event.body || '{}') as {
    filename?: string;
    contentType?: string;
    sizeBytes?: number;
  };
  const filename = (body.filename || 'document.pdf').replace(/[^\w.\- ]+/g, '_');
  const contentType = body.contentType || 'application/pdf';
  const sizeBytes = Number(body.sizeBytes || 0);
  const maxBytes = Number(MAX_UPLOAD_BYTES);

  if (!filename.toLowerCase().endsWith('.pdf')) {
    return json(400, { error: 'Only PDF files are supported' });
  }
  if (!sizeBytes || sizeBytes > maxBytes) {
    return json(400, { error: `sizeBytes required and must be <= ${maxBytes}` });
  }

  const documentId = randomUUID();
  const s3Key = `uploads/${userId}/${documentId}/${filename}`;
  const now = new Date().toISOString();

  await ddb.send(
    new PutCommand({
      TableName: DOCUMENTS_TABLE,
      Item: {
        userId,
        documentId,
        filename,
        s3Key,
        status: 'pending',
        sizeBytes,
        contentType,
        createdAt: now,
        updatedAt: now,
      },
    })
  );

  // Bucket default encryption (SSE-KMS) applies at rest.
  // Avoid signing KMS headers so browser PUTs only need Content-Type.
  const command = new PutObjectCommand({
    Bucket: DOCS_BUCKET,
    Key: s3Key,
    ContentType: contentType,
    Metadata: {
      userid: userId,
      documentid: documentId,
    },
  });

  const uploadUrl = await getSignedUrl(s3, command, { expiresIn: 900 });
  audit('document.upload_created', { userId, documentId, sizeBytes });

  return json(201, { documentId, uploadUrl, s3Key, expiresIn: 900 });
}

async function listDocuments(userId: string) {
  const result = await ddb.send(
    new QueryCommand({
      TableName: DOCUMENTS_TABLE,
      KeyConditionExpression: 'userId = :u',
      ExpressionAttributeValues: { ':u': userId },
      ScanIndexForward: false,
    })
  );
  return json(200, { documents: result.Items ?? [] });
}

async function getDocument(userId: string, documentId: string) {
  const result = await ddb.send(
    new GetCommand({
      TableName: DOCUMENTS_TABLE,
      Key: { userId, documentId },
    })
  );
  if (!result.Item) return json(404, { error: 'Document not found' });
  return json(200, { document: result.Item });
}
