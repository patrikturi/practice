import { config } from './config';
import { getAccessToken } from './auth';

async function authHeaders() {
  const token = await getAccessToken();
  if (!token) throw new Error('Not authenticated');
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

export async function listDocuments() {
  const headers = await authHeaders();
  const res = await fetch(`${config.httpApiUrl}/documents`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getDocument(id) {
  const headers = await authHeaders();
  const res = await fetch(`${config.httpApiUrl}/documents/${id}`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createUpload(filename, sizeBytes, contentType = 'application/pdf') {
  const headers = await authHeaders();
  const res = await fetch(`${config.httpApiUrl}/documents`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ filename, sizeBytes, contentType }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadPdf(file, onProgress) {
  const meta = await createUpload(file.name, file.size, file.type || 'application/pdf');
  await new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', meta.uploadUrl);
    xhr.setRequestHeader('Content-Type', file.type || 'application/pdf');
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) onProgress(e.loaded / e.total);
    };
    xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`Upload failed: ${xhr.status}`)));
    xhr.onerror = () => reject(new Error('Upload network error'));
    xhr.send(file);
  });
  return meta;
}

export async function listChats() {
  const headers = await authHeaders();
  const res = await fetch(`${config.httpApiUrl}/chats`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getChat(sessionId) {
  const headers = await authHeaders();
  const res = await fetch(`${config.httpApiUrl}/chats/${sessionId}`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function openChatSocket(onMessage) {
  const token = await getAccessToken();
  const url = `${config.wsApiUrl}?token=${encodeURIComponent(token)}`;
  const ws = new WebSocket(url);

  ws.onmessage = (evt) => {
    try {
      onMessage(JSON.parse(evt.data));
    } catch {
      onMessage({ type: 'raw', data: evt.data });
    }
  };

  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error('WebSocket connection failed'));
  });

  return ws;
}
