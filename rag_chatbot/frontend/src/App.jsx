import { useEffect, useMemo, useRef, useState } from 'react';
import { assertConfig } from './config';
import {
  confirmSignUp,
  getAccessToken,
  getSession,
  signIn,
  signOut,
  signUp,
} from './auth';
import { getChat, listChats, listDocuments, openChatSocket, uploadPdf } from './api';

function AuthPanel({ onAuthed }) {
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (mode === 'signin') {
        await signIn(email, password);
        onAuthed();
      } else if (mode === 'signup') {
        await signUp(email, password);
        setMode('confirm');
      } else {
        await confirmSignUp(email, code);
        await signIn(email, password);
        onAuthed();
      }
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <p className="brand">DocuQuery</p>
        <h1>{mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Create account' : 'Confirm email'}</h1>
        <p className="muted">Claude RAG over your private PDF knowledge base.</p>
        <form onSubmit={submit}>
          <label>
            Email
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          </label>
          {mode !== 'confirm' && (
            <label>
              Password
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                type="password"
                minLength={12}
                required
              />
            </label>
          )}
          {mode === 'confirm' && (
            <label>
              Confirmation code
              <input value={code} onChange={(e) => setCode(e.target.value)} required />
            </label>
          )}
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={busy}>
            {busy ? 'Working…' : mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Sign up' : 'Confirm'}
          </button>
        </form>
        <div className="auth-switch">
          {mode === 'signin' ? (
            <button type="button" className="link" onClick={() => setMode('signup')}>
              Need an account?
            </button>
          ) : (
            <button type="button" className="link" onClick={() => setMode('signin')}>
              Back to sign in
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [status, setStatus] = useState('idle');
  const [citations, setCitations] = useState([]);
  const [uploadPct, setUploadPct] = useState(null);
  const [error, setError] = useState('');
  const wsRef = useRef(null);
  const bottomRef = useRef(null);
  const streamingRef = useRef('');

  async function refreshSidebars() {
    const [docs, chats] = await Promise.all([listDocuments(), listChats()]);
    setDocuments(docs.documents || []);
    setSessions(chats.sessions || []);
  }

  useEffect(() => {
    refreshSidebars().catch((e) => setError(e.message));
    const id = setInterval(() => {
      listDocuments()
        .then((d) => setDocuments(d.documents || []))
        .catch(() => {});
    }, 8000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, status]);

  useEffect(() => {
    return () => wsRef.current?.close();
  }, []);

  async function ensureSocket() {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return wsRef.current;
    const ws = await openChatSocket((msg) => {
      if (msg.type === 'session') {
        setSessionId(msg.sessionId);
      } else if (msg.type === 'token') {
        streamingRef.current += msg.text || '';
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last?.role === 'assistant' && last.streaming) {
            next[next.length - 1] = { ...last, content: streamingRef.current };
          } else {
            next.push({ role: 'assistant', content: streamingRef.current, streaming: true });
          }
          return next;
        });
      } else if (msg.type === 'done') {
        setStatus('idle');
        setCitations(msg.citations || []);
        setMessages((prev) =>
          prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, streaming: false, cacheHit: msg.cacheHit } : m
          )
        );
        streamingRef.current = '';
        refreshSidebars().catch(() => {});
      } else if (msg.type === 'error') {
        setStatus('idle');
        setError(msg.message || 'Chat error');
      } else if (msg.type === 'status') {
        setStatus(msg.stage || 'working');
      }
    });
    wsRef.current = ws;
    return ws;
  }

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || status === 'generating') return;
    setError('');
    setInput('');
    setCitations([]);
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setStatus('generating');
    streamingRef.current = '';

    try {
      const ws = await ensureSocket();
      ws.send(JSON.stringify({ action: 'sendMessage', message: text, sessionId }));
    } catch (err) {
      setStatus('idle');
      setError(err.message);
    }
  }

  async function onUpload(e) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    setError('');
    setUploadPct(0);
    try {
      await uploadPdf(file, setUploadPct);
      await refreshSidebars();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploadPct(null);
    }
  }

  async function openSession(id) {
    setError('');
    const data = await getChat(id);
    setSessionId(id);
    setMessages(
      (data.messages || []).map((m) => ({
        role: m.role,
        content: m.content,
        cacheHit: m.cacheHit,
      }))
    );
    const lastAssistant = [...(data.messages || [])].reverse().find((m) => m.role === 'assistant');
    setCitations(lastAssistant?.citations || []);
  }

  function newChat() {
    setSessionId(null);
    setMessages([]);
    setCitations([]);
  }

  async function logout() {
    wsRef.current?.close();
    signOut();
    window.location.reload();
  }

  const indexedCount = useMemo(
    () => documents.filter((d) => d.status === 'indexed').length,
    [documents]
  );

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-top">
          <p className="brand">DocuQuery</p>
          <button type="button" className="ghost" onClick={newChat}>
            New chat
          </button>
        </div>
        <section>
          <h2>History</h2>
          <ul className="list">
            {sessions.map((s) => (
              <li key={s.sessionId}>
                <button type="button" className={sessionId === s.sessionId ? 'active' : ''} onClick={() => openSession(s.sessionId)}>
                  {s.title || s.sessionId}
                </button>
              </li>
            ))}
            {!sessions.length && <li className="muted">No chats yet</li>}
          </ul>
        </section>
        <section>
          <h2>Documents ({indexedCount} indexed)</h2>
          <label className="upload">
            <input type="file" accept="application/pdf" onChange={onUpload} />
            Upload PDF
          </label>
          {uploadPct != null && <div className="progress"><span style={{ width: `${Math.round(uploadPct * 100)}%` }} /></div>}
          <ul className="list docs">
            {documents.map((d) => (
              <li key={d.documentId}>
                <span>{d.filename}</span>
                <em className={`pill ${d.status}`}>{d.status}</em>
              </li>
            ))}
            {!documents.length && <li className="muted">Upload PDFs to ground answers</li>}
          </ul>
        </section>
        <button type="button" className="ghost logout" onClick={logout}>
          Sign out
        </button>
      </aside>

      <main className="chat">
        <header>
          <h1>Knowledge chat</h1>
          <p className="muted">Claude Sonnet 5.5 · Bedrock · RAG</p>
        </header>

        <div className="transcript">
          {!messages.length && (
            <div className="empty">
              <h2>Ask your documents</h2>
              <p>Upload PDFs, wait for indexing, then ask questions grounded in your knowledge base.</p>
            </div>
          )}
          {messages.map((m, i) => (
            <article key={i} className={`bubble ${m.role}`}>
              <div className="meta">
                {m.role === 'assistant' ? 'Assistant' : 'You'}
                {m.cacheHit ? <span className="pill cache">cached</span> : null}
                {m.streaming ? <span className="pill stream">streaming</span> : null}
              </div>
              <p>{m.content}</p>
            </article>
          ))}
          <div ref={bottomRef} />
        </div>

        {!!citations.length && (
          <div className="citations">
            <h3>Sources</h3>
            <ul>
              {citations.map((c) => (
                <li key={`${c.documentId}-${c.index}`}>
                  <strong>[{c.index}]</strong> {c.snippet}
                </li>
              ))}
            </ul>
          </div>
        )}

        {error && <p className="error banner">{error}</p>}

        <form className="composer" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={status === 'generating' ? 'Generating…' : 'Ask a question about your documents'}
            disabled={status === 'generating'}
          />
          <button type="submit" disabled={status === 'generating' || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default function App() {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const missing = assertConfig();

  useEffect(() => {
    getSession()
      .then(async (session) => {
        if (session) {
          const token = await getAccessToken();
          setAuthed(!!token);
        }
      })
      .finally(() => setReady(true));
  }, []);

  if (missing.length) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <p className="brand">DocuQuery</p>
          <h1>Configure environment</h1>
          <p className="muted">Copy <code>frontend/.env.example</code> to <code>frontend/.env</code> and set:</p>
          <ul>{missing.map((m) => <li key={m}><code>{m}</code></li>)}</ul>
        </div>
      </div>
    );
  }

  if (!ready) return <div className="auth-shell"><p className="muted">Loading…</p></div>;
  if (!authed) return <AuthPanel onAuthed={() => setAuthed(true)} />;
  return <ChatApp />;
}
