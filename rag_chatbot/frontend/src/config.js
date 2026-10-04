export const config = {
  region: import.meta.env.VITE_AWS_REGION || 'us-east-1',
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID || '',
  httpApiUrl: (import.meta.env.VITE_HTTP_API_URL || '').replace(/\/$/, ''),
  wsApiUrl: (import.meta.env.VITE_WS_API_URL || '').replace(/\/$/, ''),
};

export function assertConfig() {
  const missing = Object.entries(config)
    .filter(([, v]) => !v)
    .map(([k]) => k);
  return missing;
}
