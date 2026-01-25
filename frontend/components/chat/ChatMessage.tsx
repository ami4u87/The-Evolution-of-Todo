"use client";

import type { ChatMessage as ChatMessageType, ToolAction } from "@/lib/types";

interface ChatMessageProps {
  message: ChatMessageType;
  actions?: ToolAction[];
}

export default function ChatMessage({ message, actions }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-gray-100 text-gray-900 rounded-bl-md"
        }`}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>

        {/* Show actions taken by assistant */}
        {!isUser && actions && actions.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Actions taken:</p>
            <div className="space-y-1">
              {actions.map((action, index) => (
                <div
                  key={index}
                  className="text-xs bg-white/50 rounded px-2 py-1"
                >
                  <span className="font-medium text-blue-600">
                    {action.tool}
                  </span>
                  {action.result &&
                    typeof action.result === "object" &&
                    "success" in action.result && (
                      <span
                        className={`ml-2 ${
                          action.result.success
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {action.result.success ? "Success" : "Failed"}
                      </span>
                    )}
                </div>
              ))}
            </div>
          </div>
        )}

        {message.timestamp && (
          <p
            className={`text-xs mt-2 ${
              isUser ? "text-blue-200" : "text-gray-400"
            }`}
          >
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}
