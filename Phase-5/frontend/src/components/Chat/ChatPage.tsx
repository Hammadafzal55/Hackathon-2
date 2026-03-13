'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '../../lib/api';
import type {
  MessageInfo,
  ConversationSummary,
  ToolCallInfo,
  ACTIVE_CONVERSATION_KEY as _,
} from '../../types/chat';
import { ACTIVE_CONVERSATION_KEY } from '../../types/chat';

interface LocalMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCallInfo[] | null;
  created_at: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [showSidebar, setShowSidebar] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load saved conversation on mount
  useEffect(() => {
    const savedId = localStorage.getItem(ACTIVE_CONVERSATION_KEY);
    if (savedId) {
      loadConversation(savedId);
    }
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await apiClient.listConversations();
      setConversations(data.conversations);
    } catch {
      // silently fail - sidebar just shows empty
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const data = await apiClient.getConversation(id);
      setConversationId(id);
      localStorage.setItem(ACTIVE_CONVERSATION_KEY, id);
      setMessages(
        data.messages
          .filter((m: MessageInfo) => m.content)
          .map((m: MessageInfo) => ({
            id: m.id,
            role: m.role,
            content: m.content || '',
            tool_calls: m.tool_calls,
            created_at: m.created_at,
          }))
      );
      setShowSidebar(false);
    } catch {
      setError('Failed to load conversation');
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem(ACTIVE_CONVERSATION_KEY);
    setShowSidebar(false);
    setError(null);
    inputRef.current?.focus();
  };

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setError(null);
    setSending(true);
    setInput('');

    // Add user message immediately
    const userMsg: LocalMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await apiClient.sendChatMessage(text, conversationId || undefined);

      // Update conversation ID (important for new conversations)
      if (!conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem(ACTIVE_CONVERSATION_KEY, response.conversation_id);
      }

      // Add assistant message
      const assistantMsg: LocalMessage = {
        id: `resp-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        tool_calls: response.tool_calls.length > 0 ? response.tool_calls : null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Refresh conversation list
      loadConversations();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to send message';
      setError(message);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar */}
      <div
        className={`${
          showSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        } fixed md:relative z-40 w-72 h-full transition-transform duration-300 border-r border-white/20 backdrop-blur-md bg-white/5 dark:bg-gray-900/40 flex flex-col`}
      >
        {/* Sidebar header */}
        <div className="p-4 border-b border-white/10">
          <button
            onClick={startNewChat}
            className="w-full px-4 py-2.5 text-sm font-medium rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white transition-all duration-300 shadow-lg shadow-blue-500/20"
          >
            + New Chat
          </button>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-4">
              No conversations yet
            </p>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => loadConversation(conv.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm truncate transition-all duration-200 ${
                  conversationId === conv.id
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                }`}
              >
                <div className="font-medium truncate">{conv.title}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {conv.message_count} messages
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Sidebar overlay for mobile */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/20 backdrop-blur-sm bg-white/5">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="md:hidden p-2 rounded-lg hover:bg-white/10 text-gray-400"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
            AI Chat Assistant
          </h1>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.length === 0 && !sending && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-4xl mb-4">💬</div>
              <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                How can I help you manage your tasks?
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-md">
                Ask me to create, list, update, or delete tasks using natural language.
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  'What tasks do I have?',
                  'Add a task to buy groceries',
                  'Show my completed tasks',
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => {
                      setInput(prompt);
                      inputRef.current?.focus();
                    }}
                    className="px-4 py-2 text-sm rounded-full border border-white/20 bg-white/5 hover:bg-white/10 text-gray-600 dark:text-gray-300 transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
                    : 'glass border border-white/20 backdrop-blur-sm text-gray-800 dark:text-gray-200'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {msg.content}
                </div>

                {/* Tool call badges */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="mt-3 space-y-2 border-t border-white/10 pt-2">
                    {msg.tool_calls.map((tc, i) => (
                      <ToolCallBadge key={i} toolCall={tc} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {sending && (
            <div className="flex justify-start">
              <div className="glass border border-white/20 backdrop-blur-sm rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="flex justify-center">
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg px-4 py-2 text-sm">
                {error}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-white/20 backdrop-blur-sm bg-white/5 p-4">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
              disabled={sending}
              rows={1}
              className="flex-1 resize-none rounded-xl px-4 py-3 bg-white/10 dark:bg-gray-800/50 border border-white/20 focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 outline-none text-gray-800 dark:text-gray-200 placeholder-gray-500 text-sm backdrop-blur-sm transition-all disabled:opacity-50"
              style={{ maxHeight: '120px' }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 120) + 'px';
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || sending}
              className="self-end px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ToolCallBadge({ toolCall }: { toolCall: ToolCallInfo }) {
  const icons: Record<string, string> = {
    create_task: '➕',
    list_tasks: '📋',
    update_task: '✏️',
    complete_task: '✅',
    delete_task: '🗑️',
    search_tasks: '🔍',
  };

  return (
    <div
      className={`flex items-center gap-2 text-xs rounded-lg px-3 py-1.5 ${
        toolCall.success
          ? 'bg-green-500/10 text-green-400 border border-green-500/20'
          : 'bg-red-500/10 text-red-400 border border-red-500/20'
      }`}
    >
      <span>{icons[toolCall.tool_name] || '🔧'}</span>
      <span className="font-medium">{toolCall.tool_name}</span>
      {toolCall.result && (
        <span className="text-gray-400 truncate max-w-[200px]">
          — {toolCall.result}
        </span>
      )}
      <span className="ml-auto">
        {toolCall.success ? '✓' : '✗'}
      </span>
    </div>
  );
}
