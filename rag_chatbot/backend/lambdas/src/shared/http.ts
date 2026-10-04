import type {
  APIGatewayProxyEventV2,
  APIGatewayProxyEventV2WithJWTAuthorizer,
  APIGatewayProxyResultV2,
} from 'aws-lambda';

export type JsonResult = APIGatewayProxyResultV2;
export type HttpEvent = APIGatewayProxyEventV2 | APIGatewayProxyEventV2WithJWTAuthorizer;

export function json(statusCode: number, body: unknown, headers: Record<string, string> = {}): JsonResult {
  return {
    statusCode,
    headers: {
      'content-type': 'application/json',
      'access-control-allow-origin': '*',
      'access-control-allow-headers': 'authorization,content-type',
      ...headers,
    },
    body: JSON.stringify(body),
  };
}

export function getUserId(event: HttpEvent): string | null {
  const requestContext = event.requestContext as {
    authorizer?: { jwt?: { claims?: Record<string, unknown> } };
  };
  const claims = requestContext.authorizer?.jwt?.claims ?? {};
  const sub = claims.sub;
  return typeof sub === 'string' ? sub : null;
}

export function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}
