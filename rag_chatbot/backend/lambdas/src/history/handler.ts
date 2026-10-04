import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, QueryCommand } from '@aws-sdk/lib-dynamodb';
import type { APIGatewayProxyHandlerV2WithJWTAuthorizer } from 'aws-lambda';
import { getUserId, json, requireEnv } from '../shared/http.js';

const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const CHAT_SESSIONS_TABLE = requireEnv('CHAT_SESSIONS_TABLE');
const CHAT_MESSAGES_TABLE = requireEnv('CHAT_MESSAGES_TABLE');

export const handler: APIGatewayProxyHandlerV2WithJWTAuthorizer = async (event) => {
  const userId = getUserId(event);
  if (!userId) return json(401, { error: 'Unauthorized' });

  const method = event.requestContext.http.method;
  const path = event.rawPath || '';

  try {
    if (method === 'GET' && /\/chats\/[^/]+$/.test(path)) {
      const sessionId = event.pathParameters?.id;
      if (!sessionId) return json(400, { error: 'Missing session id' });
      return await getSession(userId, sessionId);
    }
    if (method === 'GET' && path.endsWith('/chats')) {
      return await listSessions(userId);
    }
    return json(404, { error: 'Not found' });
  } catch (err) {
    console.error(err);
    return json(500, { error: 'Internal error' });
  }
};

async function listSessions(userId: string) {
  const result = await ddb.send(
    new QueryCommand({
      TableName: CHAT_SESSIONS_TABLE,
      KeyConditionExpression: 'userId = :u',
      ExpressionAttributeValues: { ':u': userId },
      ScanIndexForward: false,
      Limit: 50,
    })
  );
  return json(200, { sessions: result.Items ?? [] });
}

async function getSession(userId: string, sessionId: string) {
  const sessions = await ddb.send(
    new QueryCommand({
      TableName: CHAT_SESSIONS_TABLE,
      KeyConditionExpression: 'userId = :u AND sessionId = :s',
      ExpressionAttributeValues: { ':u': userId, ':s': sessionId },
      Limit: 1,
    })
  );
  if (!sessions.Items?.length) return json(404, { error: 'Session not found' });

  const messages = await ddb.send(
    new QueryCommand({
      TableName: CHAT_MESSAGES_TABLE,
      KeyConditionExpression: 'sessionId = :s',
      ExpressionAttributeValues: { ':s': sessionId },
      ScanIndexForward: true,
    })
  );

  return json(200, {
    session: sessions.Items[0],
    messages: messages.Items ?? [],
  });
}
