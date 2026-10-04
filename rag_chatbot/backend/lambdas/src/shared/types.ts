export interface Citation {
  index: number;
  documentId: string;
  score: number;
  snippet: string;
  metadata: unknown;
}

export interface DocumentChunkRow {
  id: string;
  document_id: string;
  content: string;
  metadata: unknown;
  score: number | string;
}

export interface AuroraSecret {
  host: string;
  port: number;
  dbname: string;
  username: string;
  password: string;
}

export type WsOutboundMessage =
  | { type: 'session'; sessionId: string }
  | { type: 'token'; text: string; cacheHit?: boolean }
  | { type: 'done'; cacheHit: boolean; citations: Citation[]; latencyMs: number; sessionId: string }
  | { type: 'status'; stage: string }
  | { type: 'error'; message: string; detail?: string };
