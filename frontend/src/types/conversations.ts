export interface Conversation {
  id: string;
  company_id: string;
  user_id: string;
  title: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  image_id: string | null;
  role: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  intent: string | null;
  route: string | null;
  msg_metadata: Record<string, any>;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}
