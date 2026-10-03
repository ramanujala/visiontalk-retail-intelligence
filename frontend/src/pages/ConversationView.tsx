import React, { useEffect, useState } from 'react';
import { Conversation, ConversationDetail, Message } from '../types/conversations';
import { ImageItem } from '../types/image';
import {
  fetchConversations,
  createConversation,
  fetchConversationDetail,
  postConversationMessage,
  archiveConversation
} from '../services/conversations';
import styles from './Auth.module.css';

interface ConversationViewProps {
  token: string;
  selectedImageForContext?: ImageItem | null;
  onClearImageContext?: () => void;
}

export const ConversationView: React.FC<ConversationViewProps> = ({
  token,
  selectedImageForContext,
  onClearImageContext
}) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<ConversationDetail | null>(null);
  const [loadingList, setLoadingList] = useState<boolean>(true);
  const [loadingConv, setLoadingConv] = useState<boolean>(false);
  const [sending, setSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [inputContent, setInputContent] = useState<string>('');
  const [newTitle, setNewTitle] = useState<string>('');

  const loadConversationList = async () => {
    setLoadingList(true);
    try {
      const list = await fetchConversations(token);
      setConversations(list);
      if (list.length > 0 && !activeConv) {
        loadDetail(list[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load conversations.');
    } finally {
      setLoadingList(false);
    }
  };

  const loadDetail = async (convId: string) => {
    setLoadingConv(true);
    setError(null);
    try {
      const detail = await fetchConversationDetail(token, convId);
      setActiveConv(detail);
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation history.');
    } finally {
      setLoadingConv(false);
    }
  };

  useEffect(() => {
    loadConversationList();
  }, [token]);

  const handleCreateNew = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createConversation(token, newTitle || undefined);
      setNewTitle('');
      await loadConversationList();
      await loadDetail(created.id);
    } catch (err: any) {
      setError(err.message || 'Failed to create new conversation.');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputContent.trim() || !activeConv) return;

    setSending(true);
    setError(null);
    const contentToSend = inputContent;
    setInputContent('');

    try {
      await postConversationMessage(
        token,
        activeConv.id,
        contentToSend,
        selectedImageForContext ? selectedImageForContext.id : undefined
      );
      await loadDetail(activeConv.id);
    } catch (err: any) {
      setError(err.message || 'Failed to send message.');
    } finally {
      setSending(false);
    }
  };

  const handleArchive = async (convId: string) => {
    if (!confirm('Archive this conversation session?')) return;
    try {
      await archiveConversation(token, convId);
      if (activeConv?.id === convId) {
        setActiveConv(null);
      }
      await loadConversationList();
    } catch (err: any) {
      setError(err.message || 'Failed to archive conversation.');
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '1.5rem', width: '100%', minHeight: '600px' }} data-testid="conversation-view-page">
      {/* Sidebar: Conversation Sessions List */}
      <div className={styles.authCard} style={{ maxWidth: '100%', display: 'flex', flexDirection: 'column', height: '100%' }}>
        <h3 className={styles.authTitle} style={{ fontSize: '1.1rem', textAlign: 'left', marginBottom: '1rem' }}>
          Audit Chat Sessions
        </h3>

        <form onSubmit={handleCreateNew} style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <input
            type="text"
            className={styles.input}
            placeholder="New Chat Title..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            style={{ marginBottom: 0 }}
          />
          <button type="submit" className={styles.submitBtn} style={{ marginTop: 0, whiteSpace: 'nowrap' }}>
            + New
          </button>
        </form>

        {loadingList ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Loading chats...</p>
        ) : conversations.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No conversations yet. Create your first session above!</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto' }}>
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => loadDetail(conv.id)}
                style={{
                  padding: '0.7rem',
                  borderRadius: '6px',
                  backgroundColor: activeConv?.id === conv.id ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255,255,255,0.04)',
                  border: activeConv?.id === conv.id ? '1px solid #3b82f6' : '1px solid transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  justify: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{conv.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleArchive(conv.id);
                  }}
                  style={{ backgroundColor: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.8rem' }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Chat Panel */}
      <div className={styles.authCard} style={{ maxWidth: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%' }}>
        {activeConv ? (
          <>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.8rem', marginBottom: '1rem' }}>
                <h3 className={styles.authTitle} style={{ fontSize: '1.2rem', textAlign: 'left', margin: 0 }}>
                  {activeConv.title}
                </h3>
                {selectedImageForContext && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(99, 102, 241, 0.2)', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.8rem', color: '#818cf8' }}>
                    📷 Attached Image: <strong>{selectedImageForContext.original_filename}</strong>
                    {onClearImageContext && (
                      <button onClick={onClearImageContext} style={{ backgroundColor: 'transparent', border: 'none', color: '#818cf8', cursor: 'pointer', fontWeight: 700 }}>✕</button>
                    )}
                  </div>
                )}
              </div>

              {error && <div className={styles.errorMessage}>{error}</div>}

              {/* Messages History List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '420px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                {loadingConv ? (
                  <p style={{ color: 'var(--text-secondary)' }}>Loading messages history...</p>
                ) : activeConv.messages.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)' }}>No messages in this chat yet. Type a question below to start audit conversation.</p>
                ) : (
                  activeConv.messages.map((msg) => (
                    <div
                      key={msg.id}
                      style={{
                        alignSelf: msg.role === 'USER' ? 'flex-end' : 'flex-start',
                        maxWidth: '85%',
                        backgroundColor: msg.role === 'USER' ? 'var(--primary-color, #3b82f6)' : 'rgba(255,255,255,0.06)',
                        color: '#fff',
                        padding: '0.8rem 1rem',
                        borderRadius: '8px',
                        borderBottomRightRadius: msg.role === 'USER' ? 0 : '8px',
                        borderBottomLeftRadius: msg.role === 'ASSISTANT' ? 0 : '8px'
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', opacity: 0.7, marginBottom: '0.3rem', display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                        <span>{msg.role === 'USER' ? 'User' : `AI Assistant ${msg.intent ? `[Intent: ${msg.intent}]` : ''}`}</span>
                        <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                      <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.95rem', lineHeight: '1.5' }}>{msg.content}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSendMessage} style={{ marginTop: '1.5rem', display: 'flex', gap: '0.8rem' }}>
              <input
                type="text"
                className={styles.input}
                placeholder="Ask a retail audit question (e.g. Which products are missing? Is the shelf compliant?)..."
                value={inputContent}
                onChange={(e) => setInputContent(e.target.value)}
                style={{ marginBottom: 0 }}
                disabled={sending}
              />
              <button type="submit" className={styles.submitBtn} style={{ marginTop: 0, whiteSpace: 'nowrap' }} disabled={sending || !inputContent.trim()}>
                {sending ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-secondary)' }}>
            Select or create a chat session to start conversation.
          </div>
        )}
      </div>
    </div>
  );
};
