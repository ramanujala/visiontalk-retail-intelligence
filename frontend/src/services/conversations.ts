import { Conversation, ConversationDetail, Message } from '../types/conversations';

const API_BASE = '/api/v1';

export const createConversation = async (
  token: string,
  title?: string
): Promise<Conversation> => {
  const response = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ title: title || 'Retail Audit Chat' })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create conversation.');
  }

  return response.json();
};

export const fetchConversations = async (token: string): Promise<Conversation[]> => {
  const response = await fetch(`${API_BASE}/conversations`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch conversations.');
  }

  return response.json();
};

export const fetchConversationDetail = async (
  token: string,
  conversationId: string
): Promise<ConversationDetail> => {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch conversation detail.');
  }

  return response.json();
};

export const postConversationMessage = async (
  token: string,
  conversationId: string,
  content: string,
  imageId?: string
): Promise<Message> => {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      content,
      image_id: imageId || null
    })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to post message.');
  }

  return response.json();
};

export const archiveConversation = async (
  token: string,
  conversationId: string
): Promise<void> => {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to archive conversation.');
  }
};
