# Phase III: AI-Powered Todo Chatbot

## Overview
Add an AI-powered conversational interface for task management using OpenAI's API. Users can interact with their tasks using natural language commands.

## Feature Requirements

### 1. Conversational Interface
- Natural language task management
- Support for commands like:
  - "Add task: Buy milk tomorrow at 5 PM"
  - "List my tasks"
  - "Complete the grocery task"
  - "Reschedule morning meeting to 2 PM"
  - "Delete old tasks"
  - "What tasks are pending?"
  - "Mark 'buy groceries' as done"

### 2. Backend Chat Endpoint
- POST `/api/chat` - Process user messages
- Requires JWT authentication
- Integrates with OpenAI API
- Uses tool calls to interact with existing task endpoints

### 3. AI Agent Tools
The AI agent has access to these tools:
- `list_tasks` - List all user tasks
- `create_task` - Create a new task
- `update_task` - Update existing task
- `delete_task` - Delete a task
- `mark_complete` - Mark task as completed
- `search_tasks` - Find tasks by title/description

### 4. Frontend Chat Page
- Route: `/chat`
- Chat UI with message bubbles
- User input box with send button
- Loading states during AI processing
- Error handling with retry
- Chat history persistence (session-based)

### 5. Navigation Integration
- Add "Chat" link to dashboard header
- Optional: sidebar toggle for chat
- After chat actions, dashboard task list refreshes

## Technical Stack

### Backend
- OpenAI Python SDK (`openai>=1.0`)
- Function calling for tool use
- Streaming responses (optional)

### Frontend
- Chat component with message history
- Real-time message updates
- Tailwind CSS for styling

## API Contract

### POST /api/chat

Request:
```json
{
  "message": "Add task: Buy milk tomorrow",
  "conversation_id": "optional-uuid"
}
```

Response:
```json
{
  "response": "I've created a new task 'Buy milk' for you.",
  "conversation_id": "uuid",
  "actions_taken": [
    {
      "tool": "create_task",
      "result": { "id": "...", "title": "Buy milk", ... }
    }
  ]
}
```

## Security
- All chat endpoints require authentication
- AI has no access to other users' tasks
- Rate limiting recommended (future)

## Out of Scope
- Voice input/output
- Multi-modal input (images)
- Real-time collaboration
- Advanced NLP training

## Acceptance Criteria
- [ ] User can chat with AI to manage tasks
- [ ] All CRUD operations work via chat
- [ ] Chat UI is responsive and accessible
- [ ] Errors are handled gracefully
- [ ] README documents chatbot usage
