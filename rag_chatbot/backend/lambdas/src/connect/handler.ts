import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand } from '@aws-sdk/lib-dynamodb';
import type { APIGatewayProxyResultV2, APIGatewayProxyWebsocketHandlerV2 } from 'aws-lambda';
import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';
import { audit } from '../shared/audit.js';
import { requireEnv } from '../shared/http.js';

const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const WS_CONNECTIONS_TABLE = requireEnv('WS_CONNECTIONS_TABLE');
const COGNITO_ISSUER = process.env.COGNITO_ISSUER;
const COGNITO_CLIENT_ID = process.env.COGNITO_CLIENT_ID;

type Jwks = ReturnType<typeof createRemoteJWKSet>;
let jwks: Jwks | undefined;

function unauthorized(): APIGatewayProxyResultV2 {
  return { statusCode: 401, body: 'Unauthorized' };
}

export const handler: APIGatewayProxyWebsocketHandlerV2 = async (event) => {
  const connectionId = event.requestContext.connectionId;
  // $connect may include headers depending on the client; types omit them.
  const headers = (event as { headers?: Record<string, string | undefined> }).headers ?? {};
  const authHeader = headers.Authorization || headers.authorization || '';
  const token =
    event.queryStringParameters?.token || authHeader.replace(/^Bearer\s+/i, '');

  if (!token) {
    audit('ws.connect.denied', { reason: 'missing_token' });
    return unauthorized();
  }

  try {
    const issuer = COGNITO_ISSUER;
    if (!jwks && issuer) {
      jwks = createRemoteJWKSet(new URL(`${issuer}/.well-known/jwks.json`));
    }

    let userId: string | undefined;
    if (jwks && issuer) {
      const { payload } = await jwtVerify(token, jwks, {
        issuer,
        audience: COGNITO_CLIENT_ID || undefined,
      });
      userId = typeof payload.sub === 'string' ? payload.sub : undefined;
    } else {
      // Dev fallback: decode without verify when issuer not configured in local tests
      const payload = JSON.parse(
        Buffer.from(token.split('.')[1] ?? '', 'base64url').toString()
      ) as JWTPayload;
      userId = typeof payload.sub === 'string' ? payload.sub : undefined;
    }

    if (!userId) return unauthorized();

    const expiresAt = Math.floor(Date.now() / 1000) + 24 * 60 * 60;
    await ddb.send(
      new PutCommand({
        TableName: WS_CONNECTIONS_TABLE,
        Item: {
          connectionId,
          userId,
          connectedAt: new Date().toISOString(),
          expiresAt,
        },
      })
    );

    audit('ws.connect', { userId, connectionId });
    return { statusCode: 200, body: 'Connected' };
  } catch (err) {
    console.error(err);
    return unauthorized();
  }
};
