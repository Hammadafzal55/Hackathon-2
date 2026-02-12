/**
 * Chat API type definitions
 * Matches backend schemas from POST /api/chat, GET /api/conversations
 */

export interface ToolCallInfo {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: string;
  success: boolean;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls: ToolCallInfo[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total_count: number;
}

export interface MessageInfo {
  id: string;
  role: 'user' | 'assistant';
  content: string | null;
  tool_calls: ToolCallInfo[] | null;
  tool_call_id: string | null;
  tool_name: string | null;
  created_at: string;
}

export interface ConversationDetailResponse {
  conversation: ConversationSummary;
  messages: MessageInfo[];
}

/** localStorage key for persisting active conversation */
export const ACTIVE_CONVERSATION_KEY = 'chat-active-conversation';
