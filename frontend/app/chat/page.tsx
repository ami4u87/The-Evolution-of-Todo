"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ChatMessage from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import LoadingDots from "@/components/chat/LoadingDots";
import { sendChatMessage, ApiClientError } from "@/lib/api-client";
import type { ChatMessage as ChatMessageType, ToolAction } from "@/lib/types";

interface MessageWithActions extends ChatMessageType {
  actions?: ToolAction[];
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<MessageWithActions[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Add initial greeting
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm your AI task assistant. I can help you manage your tasks through natural language. Try saying things like:\n\n" +
          '- "Add task: Buy groceries"\n' +
          '- "List my tasks"\n' +
          '- "Mark the grocery task as complete"\n' +
          '- "What tasks are pending?"\n' +
          '- "Delete the completed tasks"',
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: MessageWithActions = {
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setError(null);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: content,
        conversation_id: conversationId,
      });

      // Update conversation ID
      setConversationId(response.conversation_id);

      // Add assistant response
      const assistantMessage: MessageWithActions = {
        role: "assistant",
        content: response.response,
        timestamp: new Date().toISOString(),
        actions: response.actions_taken,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);

      if (err instanceof ApiClientError) {
        if (err.statusCode === 401) {
          router.push("/login");
          return;
        }
        setError(err.getUserMessage());
      } else {
        setError("Failed to send message. Please try again.");
      }

      // Remove the user message if there was an error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    router.push("/");
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: "assistant",
        content:
          "Chat cleared! How can I help you with your tasks?",
        timestamp: new Date().toISOString(),
      },
    ]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">
                AI Assistant
              </h1>
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                Beta
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Dashboard
              </Link>
              <button
                onClick={handleClearChat}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Clear Chat
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          <div className="space-y-2">
            {messages.map((msg, index) => (
              <ChatMessage
                key={index}
                message={msg}
                actions={msg.actions}
              />
            ))}
            {isLoading && <LoadingDots />}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </main>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask me to manage your tasks..."
          />
          <p className="text-xs text-gray-400 mt-2 text-center">
            AI responses may not always be accurate. Verify important actions.
          </p>
        </div>
      </div>
    </div>
  );
}
