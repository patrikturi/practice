import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import type { APIGatewayProxyWebsocketHandlerV2 } from 'aws-lambda';
import { audit } from '../shared/audit.js';
import { requireEnv } from '../shared/http.js';

const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const WS_CONNECTIONS_TABLE = requireEnv('WS_CONNECTIONS_TABLE');

export const handler: APIGatewayProxyWebsocketHandlerV2 = async (event) => {
  const connectionId = event.requestContext.connectionId;
  try {
    await ddb.send(
      new DeleteCommand({
        TableName: WS_CONNECTIONS_TABLE,
        Key: { connectionId },
      })
    );
    audit('ws.disconnect', { connectionId });
  } catch (err) {
    console.error(err);
  }
  return { statusCode: 200, body: 'Disconnected' };
};
