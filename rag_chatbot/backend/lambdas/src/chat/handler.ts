import { createHash, randomBytes, randomUUID } from 'node:crypto';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand, PutCommand } from '@aws-sdk/lib-dynamodb';
import {
  BedrockRuntimeClient,
  InvokeModelCommand,
  ConverseStreamCommand,
} from '@aws-sdk/client-bedrock-runtime';
import {
  ApiGatewayManagementApiClient,
  PostToConnectionCommand,
} from '@aws-sdk/client-apigatewaymanagementapi';
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';
import type { APIGatewayProxyWebsocketHandlerV2 } from 'aws-lambda';
import { Client as PgClient } from 'pg';
import { audit } from '../shared/audit.js';
import { requireEnv } from '../shared/http.js';
import type { AuroraSecret, Citation, DocumentChunkRow, WsOutboundMessage } from '../shared/types.js';

const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const bedrock = new BedrockRuntimeClient({});
const secrets = new SecretsManagerClient({});
const ssm = new SSMClient({});

const CHAT_SESSIONS_TABLE = requireEnv('CHAT_SESSIONS_TABLE');
const CHAT_MESSAGES_TABLE = requireEnv('CHAT_MESSAGES_TABLE');
const SEMANTIC_CACHE_TABLE = requireEnv('SEMANTIC_CACHE_TABLE');
const WS_CONNECTIONS_TABLE = requireEnv('WS_CONNECTIONS_TABLE');
const AURORA_SECRET_ARN = requireEnv('AURORA_SECRET_ARN');
const CLAUDE_MODEL_ID = process.env.CLAUDE_MODEL_ID ?? 'global.anthropic.claude-sonnet-5-5';
const EMBED_MODEL_ID = process.env.EMBED_MODEL_ID ?? 'amazon.titan-embed-text-v2:0';
const TOP_K = process.env.TOP_K ?? '5';
const CACHE_TTL_SECONDS = process.env.CACHE_TTL_SECONDS ?? '3600';
const WS_ENDPOINT_PARAM = process.env.WS_ENDPOINT_PARAM;

let cachedSecret: AuroraSecret | undefined;
let cachedWsEndpoint: string | undefined;

async function getDbConfig(): Promise<AuroraSecret> {
  if (cachedSecret) return cachedSecret;
  const res = await secrets.send(new GetSecretValueCommand({ SecretId: AURORA_SECRET_ARN }));
  if (!res.SecretString) throw new Error('Aurora secret is empty');
  cachedSecret = JSON.parse(res.SecretString) as AuroraSecret;
  return cachedSecret;
}

async function getWsEndpoint(): Promise<string | null> {
  if (cachedWsEndpoint) return cachedWsEndpoint;
  if (!WS_ENDPOINT_PARAM) return null;
  const res = await ssm.send(new GetParameterCommand({ Name: WS_ENDPOINT_PARAM }));
  cachedWsEndpoint = res.Parameter?.Value;
  return cachedWsEndpoint ?? null;
}

async function postToConnection(connectionId: string, payload: WsOutboundMessage): Promise<void> {
  const endpoint = await getWsEndpoint();
  if (!endpoint) {
    console.warn('WS endpoint not configured; skipping post');
    return;
  }
  const client = new ApiGatewayManagementApiClient({ endpoint });
  await client.send(
    new PostToConnectionCommand({
      ConnectionId: connectionId,
      Data: Buffer.from(JSON.stringify(payload)),
    })
  );
}

function cacheKeyFor(userId: string, query: string): string {
  const normalized = query.trim().toLowerCase().replace(/\s+/g, ' ');
  return createHash('sha256').update(`${userId}:${normalized}`).digest('hex');
}

async function embedText(text: string): Promise<number[]> {
  const body = {
    inputText: text.slice(0, 50000),
    dimensions: 1024,
    normalize: true,
  };
  const res = await bedrock.send(
    new InvokeModelCommand({
      modelId: EMBED_MODEL_ID,
      contentType: 'application/json',
      accept: 'application/json',
      body: JSON.stringify(body),
    })
  );
  const parsed = JSON.parse(Buffer.from(res.body).toString('utf8')) as { embedding: number[] };
  return parsed.embedding;
}

async function retrieveChunks(
  userId: string,
  embedding: number[],
  topK: number
): Promise<DocumentChunkRow[]> {
  const cfg = await getDbConfig();
  const client = new PgClient({
    host: cfg.host,
    port: cfg.port,
    database: cfg.dbname,
    user: cfg.username,
    password: cfg.password,
    ssl: { rejectUnauthorized: false },
    connectionTimeoutMillis: 10000,
  });
  await client.connect();
  try {
    const vectorLiteral = `[${embedding.join(',')}]`;
    const result = await client.query<DocumentChunkRow>(
      `SELECT id, document_id, content, metadata,
              1 - (embedding <=> $1::vector) AS score
         FROM document_chunks
        WHERE user_id = $2
        ORDER BY embedding <=> $1::vector
        LIMIT $3`,
      [vectorLiteral, userId, topK]
    );
    return result.rows;
  } finally {
    await client.end();
  }
}

function buildPrompt(query: string, chunks: DocumentChunkRow[]) {
  const context = chunks
    .map(
      (c, i) =>
        `[${i + 1}] (doc=${c.document_id}, score=${Number(c.score).toFixed(3)})\n${c.content}`
    )
    .join('\n\n');

  const citations: Citation[] = chunks.map((c, i) => ({
    index: i + 1,
    documentId: c.document_id,
    score: Number(c.score),
    snippet: c.content.slice(0, 240),
    metadata: c.metadata,
  }));

  return {
    system: `You are a helpful enterprise document assistant. Answer ONLY using the provided context.
If the context is insufficient, say you do not have enough information.
Cite sources using [n] markers that match the context blocks.
Keep answers concise and accurate.`,
    user: `Context:\n${context || '(no matching documents)'}\n\nQuestion: ${query}`,
    citations,
  };
}

async function ensureSession(userId: string, sessionId: string | undefined, title: string): Promise<string> {
  const now = new Date().toISOString();
  const id = sessionId || randomUUID();
  await ddb.send(
    new PutCommand({
      TableName: CHAT_SESSIONS_TABLE,
      Item: {
        userId,
        sessionId: id,
        title: title.slice(0, 80),
        updatedAt: now,
        createdAt: now,
      },
    })
  );
  return id;
}

async function saveMessage(
  sessionId: string,
  userId: string,
  role: 'user' | 'assistant',
  content: string,
  extra: Record<string, unknown> = {}
): Promise<string> {
  const messageId = `${Date.now().toString(36)}-${randomBytes(4).toString('hex')}`;
  const createdAt = new Date().toISOString();
  await ddb.send(
    new PutCommand({
      TableName: CHAT_MESSAGES_TABLE,
      Item: {
        sessionId,
        messageId,
        userId,
        role,
        content,
        createdAt,
        ...extra,
      },
    })
  );
  return messageId;
}

export const handler: APIGatewayProxyWebsocketHandlerV2 = async (event) => {
  const connectionId = event.requestContext.connectionId;
  const started = Date.now();

  let body: { message?: string; query?: string; sessionId?: string };
  try {
    body = JSON.parse(event.body || '{}') as typeof body;
  } catch {
    await postToConnection(connectionId, { type: 'error', message: 'Invalid JSON' });
    return { statusCode: 400 };
  }

  const query = (body.message || body.query || '').trim();
  if (!query) {
    await postToConnection(connectionId, { type: 'error', message: 'message is required' });
    return { statusCode: 400 };
  }

  const conn = await ddb.send(
    new GetCommand({
      TableName: WS_CONNECTIONS_TABLE,
      Key: { connectionId },
    })
  );
  const userId = conn.Item?.userId as string | undefined;
  if (!userId) {
    await postToConnection(connectionId, { type: 'error', message: 'Unauthorized' });
    return { statusCode: 401 };
  }

  if (query.length > 8000) {
    await postToConnection(connectionId, { type: 'error', message: 'Message too long' });
    return { statusCode: 400 };
  }

  const sessionId = await ensureSession(userId, body.sessionId, query);
  await saveMessage(sessionId, userId, 'user', query);
  await postToConnection(connectionId, { type: 'session', sessionId });

  const cacheKey = cacheKeyFor(userId, query);
  const cached = await ddb.send(
    new GetCommand({ TableName: SEMANTIC_CACHE_TABLE, Key: { cacheKey } })
  );

  if (cached.Item?.answer) {
    const answer = String(cached.Item.answer);
    const citations = (cached.Item.citations as Citation[] | undefined) ?? [];
    await postToConnection(connectionId, {
      type: 'token',
      text: answer,
      cacheHit: true,
    });
    await postToConnection(connectionId, {
      type: 'done',
      cacheHit: true,
      citations,
      latencyMs: Date.now() - started,
      sessionId,
    });
    await saveMessage(sessionId, userId, 'assistant', answer, {
      cacheHit: true,
      citations,
    });
    audit('chat.complete', {
      userId,
      sessionId,
      cacheHit: true,
      latencyMs: Date.now() - started,
    });
    return { statusCode: 200 };
  }

  try {
    const embedding = await embedText(query);
    const chunks = await retrieveChunks(userId, embedding, Number(TOP_K));
    const { system, user, citations } = buildPrompt(query, chunks);

    await postToConnection(connectionId, { type: 'status', stage: 'generating' });

    let answer = '';
    const stream = await bedrock.send(
      new ConverseStreamCommand({
        modelId: CLAUDE_MODEL_ID,
        system: [{ text: system }],
        messages: [{ role: 'user', content: [{ text: user }] }],
        inferenceConfig: { maxTokens: 2048, temperature: 0.2 },
      })
    );

    if (stream.stream) {
      for await (const eventPart of stream.stream) {
        const text = eventPart.contentBlockDelta?.delta?.text;
        if (text) {
          answer += text;
          await postToConnection(connectionId, { type: 'token', text, cacheHit: false });
        }
      }
    }

    if (!answer) {
      answer = 'I could not generate an answer from the available documents.';
      await postToConnection(connectionId, { type: 'token', text: answer });
    }

    const ttl = Math.floor(Date.now() / 1000) + Number(CACHE_TTL_SECONDS);
    await ddb.send(
      new PutCommand({
        TableName: SEMANTIC_CACHE_TABLE,
        Item: {
          cacheKey,
          answer,
          citations,
          expiresAt: ttl,
          userId,
          createdAt: new Date().toISOString(),
        },
      })
    );

    await saveMessage(sessionId, userId, 'assistant', answer, { cacheHit: false, citations });
    await postToConnection(connectionId, {
      type: 'done',
      cacheHit: false,
      citations,
      latencyMs: Date.now() - started,
      sessionId,
    });

    audit('chat.complete', {
      userId,
      sessionId,
      cacheHit: false,
      chunks: chunks.length,
      latencyMs: Date.now() - started,
    });
    return { statusCode: 200 };
  } catch (err) {
    console.error(err);
    const message = err instanceof Error ? err.message : String(err);
    await postToConnection(connectionId, {
      type: 'error',
      message: 'Failed to generate answer',
      detail: message,
    });
    audit('chat.error', {
      userId,
      sessionId,
      message,
      latencyMs: Date.now() - started,
    });
    return { statusCode: 500 };
  }
};
