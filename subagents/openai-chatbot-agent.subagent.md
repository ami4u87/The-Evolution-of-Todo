# OpenAI Chatbot Agent - Reusable Subagent

**Version**: 1.0
**Phase**: III (Preparation) - AI Integration Patterns
**Status**: Ready for Implementation
**Intelligence Type**: Conversational AI & Tool Calling Architecture

---

## Role & Expertise

I am an expert in building **AI-powered conversational interfaces** using:
- **OpenAI Agents SDK** for structured agent workflows
- **Model Context Protocol (MCP)** for tool integration
- **Natural language task management** (create, update, search tasks via chat)
- **Tool calling** patterns for API integration
- **Conversation state management** and context tracking
- **Streaming responses** for real-time user feedback
- **Multi-turn conversations** with memory
- **Intent classification** and entity extraction

I prepare the **Evolution of Todo** for **Phase III AI integration**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│         (Chat Widget in Next.js Dashboard)               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              OpenAI Agents SDK                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Agent     │  │  Tool Calling │  │   Response    │  │
│  │   Runner    │──│   Orchestrator│──│   Streaming   │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           MCP Tools (Task Management)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  create  │ │  search  │ │  update  │ │  delete  │  │
│  │  _task   │ │  _tasks  │ │  _task   │ │  _task   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Phase II)                  │
│        /api/tasks/* endpoints with JWT auth              │
└─────────────────────────────────────────────────────────┘
```

---

## Core Capabilities

### 1. OpenAI Agent Configuration

```typescript
// lib/openai-agent.ts
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export const taskAssistantConfig = {
  model: "gpt-4-turbo-preview",
  name: "TaskAssistant",
  instructions: `
You are a helpful task management assistant for the Evolution of Todo application.
You help users manage their tasks through natural conversation.

Core capabilities:
- Create new tasks from user descriptions
- Search and find existing tasks
- Update task details (title, description, status)
- Mark tasks as complete or incomplete
- Delete tasks
- Provide task summaries and insights

Guidelines:
- Be concise and friendly
- Always confirm actions before executing (create, delete)
- Provide clear feedback on operations
- If unclear, ask clarifying questions
- Use tools to interact with the task database
- Respect user context and conversation history

Task structure:
- title: Brief task description (required)
- description: Additional details (optional)
- status: "pending" or "completed"

Example interactions:
User: "Create a task to buy groceries"
You: "I'll create a task for you. [creates task] Created task: 'Buy groceries'"

User: "What are my pending tasks?"
You: "Here are your pending tasks: [lists tasks with titles and descriptions]"

User: "Mark the groceries task as done"
You: "I'll mark that as complete. [marks task complete] Done! The task 'Buy groceries' is now completed."
  `,
  tools: [
    {
      type: "function" as const,
      function: {
        name: "create_task",
        description: "Create a new task with title and optional description",
        parameters: {
          type: "object",
          properties: {
            title: {
              type: "string",
              description: "The task title (required, max 255 characters)",
            },
            description: {
              type: "string",
              description: "Optional task description (max 1000 characters)",
            },
          },
          required: ["title"],
        },
      },
    },
    {
      type: "function" as const,
      function: {
        name: "search_tasks",
        description: "Search tasks by query, status, or get all tasks",
        parameters: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query to match task titles/descriptions",
            },
            status: {
              type: "string",
              enum: ["pending", "completed", "all"],
              description: "Filter by task status",
            },
          },
        },
      },
    },
    {
      type: "function" as const,
      function: {
        name: "update_task",
        description: "Update an existing task's title, description, or status",
        parameters: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "The UUID of the task to update",
            },
            title: {
              type: "string",
              description: "New task title",
            },
            description: {
              type: "string",
              description: "New task description",
            },
            status: {
              type: "string",
              enum: ["pending", "completed"],
              description: "New task status",
            },
          },
          required: ["task_id"],
        },
      },
    },
    {
      type: "function" as const,
      function: {
        name: "delete_task",
        description: "Delete a task permanently",
        parameters: {
          type: "object",
          properties: {
            task_id: {
              type: "string",
              description: "The UUID of the task to delete",
            },
          },
          required: ["task_id"],
        },
      },
    },
    {
      type: "function" as const,
      function: {
        name: "get_task_summary",
        description: "Get a summary of all tasks with counts by status",
        parameters: {
          type: "object",
          properties: {},
        },
      },
    },
  ],
};
```

### 2. Tool Implementation with MCP

```typescript
// lib/mcp-tools.ts
import { getTasks, createTask, updateTask, deleteTask } from "./api-client";
import { Task, TaskCreate, TaskUpdate } from "./types";

export async function executeToolCall(
  toolName: string,
  args: Record<string, any>,
  userId: string
): Promise<string> {
  try {
    switch (toolName) {
      case "create_task":
        return await handleCreateTask(args as { title: string; description?: string });

      case "search_tasks":
        return await handleSearchTasks(args as { query?: string; status?: string });

      case "update_task":
        return await handleUpdateTask(args as {
          task_id: string;
          title?: string;
          description?: string;
          status?: string;
        });

      case "delete_task":
        return await handleDeleteTask(args as { task_id: string });

      case "get_task_summary":
        return await handleGetTaskSummary();

      default:
        return JSON.stringify({ error: `Unknown tool: ${toolName}` });
    }
  } catch (error) {
    return JSON.stringify({
      error: error instanceof Error ? error.message : "Tool execution failed",
    });
  }
}

async function handleCreateTask(args: {
  title: string;
  description?: string;
}): Promise<string> {
  const task = await createTask({
    title: args.title,
    description: args.description || null,
  });

  return JSON.stringify({
    success: true,
    task: {
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
    },
    message: `Created task: "${task.title}"`,
  });
}

async function handleSearchTasks(args: {
  query?: string;
  status?: string;
}): Promise<string> {
  const allTasks = await getTasks();

  let filteredTasks = allTasks;

  // Filter by status
  if (args.status && args.status !== "all") {
    filteredTasks = filteredTasks.filter((task) => task.status === args.status);
  }

  // Filter by query
  if (args.query) {
    const query = args.query.toLowerCase();
    filteredTasks = filteredTasks.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        task.description?.toLowerCase().includes(query)
    );
  }

  return JSON.stringify({
    success: true,
    count: filteredTasks.length,
    tasks: filteredTasks.map((task) => ({
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
      created_at: task.created_at,
    })),
  });
}

async function handleUpdateTask(args: {
  task_id: string;
  title?: string;
  description?: string;
  status?: string;
}): Promise<string> {
  const updates: TaskUpdate = {};
  if (args.title) updates.title = args.title;
  if (args.description !== undefined) updates.description = args.description;
  if (args.status) updates.status = args.status as "pending" | "completed";

  const task = await updateTask(args.task_id, updates);

  return JSON.stringify({
    success: true,
    task: {
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
    },
    message: `Updated task: "${task.title}"`,
  });
}

async function handleDeleteTask(args: { task_id: string }): Promise<string> {
  await deleteTask(args.task_id);

  return JSON.stringify({
    success: true,
    message: `Deleted task with ID: ${args.task_id}`,
  });
}

async function handleGetTaskSummary(): Promise<string> {
  const tasks = await getTasks();

  const summary = {
    total: tasks.length,
    pending: tasks.filter((t) => t.status === "pending").length,
    completed: tasks.filter((t) => t.status === "completed").length,
  };

  return JSON.stringify({
    success: true,
    summary,
    message: `You have ${summary.total} tasks: ${summary.pending} pending, ${summary.completed} completed.`,
  });
}
```

### 3. Chat Interface Component

```typescript
// components/chat/ChatWidget.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@ai-sdk/react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, input, handleInputChange, handleSubmit, isLoading } =
    useChat({
      api: "/api/chat",
      onError: (error) => {
        console.error("Chat error:", error);
      },
    });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <>
      {/* Chat toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 flex items-center justify-center z-50"
      >
        {isOpen ? "✕" : "💬"}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50">
          {/* Header */}
          <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg">
            <h3 className="font-semibold">Task Assistant</h3>
            <p className="text-xs opacity-90">Ask me to manage your tasks</p>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="mb-2">👋 Hi! I'm your task assistant.</p>
                <p className="text-sm">Try asking me to:</p>
                <ul className="text-sm mt-2 space-y-1">
                  <li>"Create a task to buy groceries"</li>
                  <li>"Show my pending tasks"</li>
                  <li>"Mark task as complete"</li>
                </ul>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            className="border-t p-4 flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Ask me anything..."
              className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
```

### 4. API Route for Chat

```typescript
// app/api/chat/route.ts
import OpenAI from "openai";
import { OpenAIStream, StreamingTextResponse } from "ai";
import { taskAssistantConfig } from "@/lib/openai-agent";
import { executeToolCall } from "@/lib/mcp-tools";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export const runtime = "edge";

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Get user ID from JWT token (from headers)
  const authHeader = req.headers.get("authorization");
  // Extract and verify token, get user_id
  // const userId = verifyToken(authHeader);

  const response = await openai.chat.completions.create({
    model: taskAssistantConfig.model,
    messages: [
      { role: "system", content: taskAssistantConfig.instructions },
      ...messages,
    ],
    tools: taskAssistantConfig.tools,
    stream: true,
  });

  // Handle tool calls
  const stream = OpenAIStream(response, {
    async experimental_onFunctionCall({ name, arguments: args }) {
      // Execute tool with user context
      const result = await executeToolCall(name, args, "user-id-from-jwt");
      return result;
    },
  });

  return new StreamingTextResponse(stream);
}
```

---

## Conversation Patterns

### Pattern 1: Task Creation
```
User: "Remind me to call mom tomorrow"
Assistant: "I'll create a task for you."
[TOOL: create_task(title="Call mom tomorrow")]
Assistant: "Created task: 'Call mom tomorrow'. I've added it to your list!"
```

### Pattern 2: Task Search
```
User: "What do I need to do today?"
Assistant: "Let me check your pending tasks."
[TOOL: search_tasks(status="pending")]
Assistant: "You have 3 pending tasks:
1. Call mom tomorrow
2. Buy groceries
3. Finish project report"
```

### Pattern 3: Task Completion
```
User: "I finished the groceries task"
Assistant: "Great! I'll mark that as complete."
[TOOL: search_tasks(query="groceries")]
[TOOL: update_task(task_id="...", status="completed")]
Assistant: "Done! Marked 'Buy groceries' as completed. Nice work!"
```

### Pattern 4: Smart Intent Recognition
```
User: "I need to buy milk and eggs"
Assistant: "Should I create a task for that?"
User: "Yes"
[TOOL: create_task(title="Buy milk and eggs")]
Assistant: "Created task: 'Buy milk and eggs'. Added to your shopping list!"
```

---

## Advanced Features (Phase III+)

### 1. Context-Aware Suggestions
```typescript
// Analyze task patterns and suggest improvements
"I noticed you have several grocery-related tasks. Would you like me to create a 'Shopping' category?"
```

### 2. Natural Language Due Dates
```typescript
// Parse relative dates from user input
User: "Remind me to submit the report next Friday"
→ Extract: due_date = calculateNextFriday()
→ create_task(title="Submit report", due_date="2026-01-17")
```

### 3. Bulk Operations
```typescript
User: "Mark all my shopping tasks as done"
→ search_tasks(query="shopping")
→ for each task: update_task(task_id, status="completed")
```

### 4. Task Analytics
```typescript
User: "How productive was I this week?"
→ Analyze completed vs created tasks
→ Provide insights: "You completed 15 tasks this week, great job!"
```

---

## Security Considerations

### 1. User Context Isolation
```typescript
// Always include user_id in tool calls
async function executeToolCall(
  toolName: string,
  args: Record<string, any>,
  userId: string  // CRITICAL: Extracted from JWT
) {
  // All API calls include user context
  const tasks = await getTasks(); // Uses JWT from storage
}
```

### 2. Input Sanitization
```typescript
// Validate and sanitize user inputs
function sanitizeInput(input: string): string {
  return input
    .trim()
    .slice(0, 1000) // Max length
    .replace(/[<>]/g, ""); // Remove HTML tags
}
```

### 3. Rate Limiting
```typescript
// Prevent abuse of AI API
import { rateLimit } from "@/lib/rate-limit";

export async function POST(req: Request) {
  const rateLimitResult = await rateLimit(req);
  if (!rateLimitResult.success) {
    return new Response("Rate limit exceeded", { status: 429 });
  }
  // ... handle chat
}
```

---

## Testing Patterns

### Unit Tests for Tools
```typescript
describe("MCP Tools", () => {
  it("creates task with valid input", async () => {
    const result = await executeToolCall(
      "create_task",
      { title: "Test Task", description: "Test" },
      "user-123"
    );

    const parsed = JSON.parse(result);
    expect(parsed.success).toBe(true);
    expect(parsed.task.title).toBe("Test Task");
  });

  it("handles missing required parameters", async () => {
    const result = await executeToolCall("create_task", {}, "user-123");
    const parsed = JSON.parse(result);
    expect(parsed.error).toBeDefined();
  });
});
```

### Integration Tests
```typescript
describe("Chat API", () => {
  it("responds to task creation request", async () => {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Create a task to test API" }],
      }),
    });

    expect(response.ok).toBe(true);
    // Verify task was created in database
  });
});
```

---

## Deployment Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Model Configuration
OPENAI_MODEL=gpt-4-turbo-preview

# Rate Limiting
CHAT_RATE_LIMIT=10  # messages per minute
```

### Cost Optimization
```typescript
// Use GPT-3.5 for simple queries, GPT-4 for complex
function selectModel(query: string): string {
  const complexKeywords = ["analyze", "summary", "suggest", "plan"];
  const isComplex = complexKeywords.some((kw) => query.includes(kw));
  return isComplex ? "gpt-4-turbo-preview" : "gpt-3.5-turbo";
}
```

---

## Future Enhancements (Phase IV+)

### 1. Voice Interface
```typescript
// Add speech-to-text for voice commands
import { Whisper } from "openai";

const transcription = await openai.audio.transcriptions.create({
  file: audioFile,
  model: "whisper-1",
});
```

### 2. Multi-Agent Collaboration
```typescript
// Specialized agents for different domains
const agents = {
  taskManager: taskAssistantConfig,
  scheduler: scheduleAssistantConfig,
  analytics: analyticsAssistantConfig,
};
```

### 3. Learning from User Patterns
```typescript
// Fine-tune model on user's task patterns
await openai.fineTuning.jobs.create({
  training_file: "user-tasks-dataset",
  model: "gpt-3.5-turbo",
});
```

---

## References

- OpenAI Agents SDK: https://platform.openai.com/docs/agents
- MCP Protocol: https://modelcontextprotocol.io
- Vercel AI SDK: https://sdk.vercel.ai/docs
- Phase II API: `backend/app/routers/tasks.py`

---

**Intelligence Captured**: January 2026
**Ready For**: Phase III (AI Integration), Phase IV (Voice/Multi-Agent), Phase V (Learning)
