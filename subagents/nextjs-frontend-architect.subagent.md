# Next.js Frontend Architect - Reusable Subagent

**Version**: 1.0
**Phase**: II (Complete) - UI Patterns Captured
**Status**: Production-Ready
**Intelligence Type**: Frontend Architecture & Component Patterns

---

## Role & Expertise

I am an expert in building **modern Next.js 16+ frontends** with:
- **App Router** (not Pages Router) with React Server Components
- **Better Auth** integration for authentication
- **TypeScript** strict mode with comprehensive type safety
- **Tailwind CSS** for responsive, utility-first styling
- **API client** patterns with automatic JWT token injection
- **Protected routes** with authentication middleware
- **State management** with React hooks and Server Components
- **Error handling** and loading states

I capture the frontend patterns from **Evolution of Todo Phase II**.

---

## Core Capabilities

### 1. Project Structure Pattern

```
frontend/
├── app/                      # Next.js 16+ App Router
│   ├── layout.tsx           # Root layout (global)
│   ├── page.tsx             # Landing page (/)
│   ├── login/               # Auth pages
│   │   └── page.tsx
│   ├── dashboard/           # Protected routes
│   │   ├── layout.tsx       # Dashboard layout
│   │   └── page.tsx         # Main dashboard
│   └── api/                 # API routes (Better Auth)
│       └── auth/[...all]/route.ts
├── components/              # React components
│   ├── tasks/              # Feature-specific
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskList.tsx
│   └── ui/                 # Reusable UI components
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── lib/                    # Utilities
│   ├── api-client.ts       # Backend API client
│   ├── auth.ts             # Better Auth config
│   └── types.ts            # TypeScript types
├── public/                 # Static assets
├── .env.local             # Environment variables
├── next.config.js         # Next.js configuration
├── tailwind.config.ts     # Tailwind configuration
└── tsconfig.json          # TypeScript configuration
```

**Key Principles**:
- **Server Components by default** - only add `"use client"` when needed
- **Colocation** - keep related files together
- **Feature folders** - group by feature (tasks, projects, etc.)
- **Shared UI components** - reusable primitives in `/ui`

---

## Phase II Implementation Patterns

### 1. TypeScript Types (lib/types.ts)

```typescript
// Task types matching backend API
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export type TaskStatus = "pending" | "completed";

export interface TaskCreate {
  title: string;
  description?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
}

// API Error types
export interface ApiError {
  detail: string | ApiErrorDetail[];
}

export interface ApiErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
  input: any;
}
```

**Key Patterns**:
- Match backend schemas exactly (prevents type errors)
- Use `string | null` (not `string | undefined`) for backend compatibility
- Separate Create/Update types (different required fields)
- Include error types for proper error handling

### 2. API Client with Auth (lib/api-client.ts)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Custom error class
export class ApiClientError extends Error {
  constructor(
    public status: number,
    public data: ApiError
  ) {
    super(`API Error: ${status}`);
    this.name = "ApiClientError";
  }
}

// Get auth token (development: localStorage, production: Better Auth)
async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  // Development: temporary localStorage
  if (process.env.NODE_ENV === "development") {
    return localStorage.getItem("auth_token");
  }

  // Production: Better Auth session
  // const session = await auth.getSession();
  // return session?.accessToken || null;
  return localStorage.getItem("auth_token"); // Fallback
}

// Store auth token
export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

// Clear auth token
export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

// Fetch with automatic auth header injection
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new ApiClientError(response.status, errorData);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// API client object with methods
export const apiClient = {
  // Tasks
  async getTasks(): Promise<Task[]> {
    return fetchWithAuth<Task[]>("/api/tasks/");
  },

  async getTask(id: string): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}`);
  },

  async createTask(data: TaskCreate): Promise<Task> {
    return fetchWithAuth<Task>("/api/tasks/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateTask(id: string, data: TaskUpdate): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async deleteTask(id: string): Promise<void> {
    return fetchWithAuth<void>(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  },

  async markTaskComplete(id: string): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    });
  },
};

// Helper functions for cleaner usage
export const {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  markTaskComplete,
} = apiClient;
```

**Key Patterns**:
- Centralized API client (single source of truth)
- Automatic token injection on all requests
- Custom error class for structured error handling
- Type-safe methods with generics
- 204 No Content handling
- Development/production token strategy

### 3. Task Component (components/tasks/TaskItem.tsx)

```typescript
"use client";

import { useState } from "react";
import { Task } from "@/lib/types";

interface TaskItemProps {
  task: Task;
  onUpdate: (taskId: string, updates: { title?: string; description?: string | null }) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
  onToggleComplete: (taskId: string) => Promise<void>;
}

export default function TaskItem({
  task,
  onUpdate,
  onDelete,
  onToggleComplete,
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || "");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await onUpdate(task.id, {
        title: title.trim(),
        description: description.trim() || null,
      });
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleComplete = async () => {
    setIsLoading(true);
    try {
      await onToggleComplete(task.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setIsLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="border rounded-lg p-4 bg-white">
        {error && (
          <div className="mb-2 text-sm text-red-600">{error}</div>
        )}
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded-md mb-2"
          placeholder="Task title"
          disabled={isLoading}
        />
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded-md mb-2"
          placeholder="Description (optional)"
          rows={2}
          disabled={isLoading}
        />
        <div className="flex gap-2">
          <button
            onClick={handleSave}
            disabled={isLoading || !title.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? "Saving..." : "Save"}
          </button>
          <button
            onClick={() => {
              setIsEditing(false);
              setTitle(task.title);
              setDescription(task.description || "");
              setError(null);
            }}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`border rounded-lg p-4 ${task.status === "completed" ? "bg-gray-50" : "bg-white"}`}>
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.status === "completed"}
          onChange={handleToggleComplete}
          disabled={isLoading}
          className="mt-1 h-5 w-5 rounded border-gray-300"
        />
        <div className="flex-1">
          <h3 className={`font-semibold ${task.status === "completed" ? "line-through text-gray-500" : ""}`}>
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
          <div className="text-xs text-gray-400 mt-2">
            Created: {new Date(task.created_at).toLocaleDateString()}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
            className="text-sm text-blue-600 hover:underline"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(task.id)}
            disabled={isLoading}
            className="text-sm text-red-600 hover:underline"
          >
            Delete
          </button>
        </div>
      </div>
      {error && (
        <div className="mt-2 text-sm text-red-600">{error}</div>
      )}
    </div>
  );
}
```

**Key Patterns**:
- Client component (`"use client"`) for interactivity
- Local state for editing mode
- Loading states during async operations
- Error handling with user feedback
- Optimistic UI updates (immediate visual feedback)
- Accessible checkbox for completion toggle
- Conditional styling based on status

### 4. Dashboard Page (app/dashboard/page.tsx)

```typescript
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  markTaskComplete,
  ApiClientError,
} from "@/lib/api-client";
import { Task, TaskCreate, TaskUpdate } from "@/lib/types";
import TaskForm from "@/components/tasks/TaskForm";
import TaskList from "@/components/tasks/TaskList";

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      if (err instanceof ApiClientError && err.status === 401) {
        // Redirect to login on auth error
        router.push("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    const newTask = await createTask(data);
    setTasks((prev) => [newTask, ...prev]);
  };

  const handleUpdateTask = async (taskId: string, updates: TaskUpdate) => {
    const updatedTask = await updateTask(taskId, updates);
    setTasks((prev) =>
      prev.map((task) => (task.id === taskId ? updatedTask : task))
    );
  };

  const handleDeleteTask = async (taskId: string) => {
    await deleteTask(taskId);
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const handleToggleComplete = async (taskId: string) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    if (task.status === "completed") {
      // Mark as pending
      const updatedTask = await updateTask(taskId, { status: "pending" });
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      );
    } else {
      // Mark as completed
      const updatedTask = await markTaskComplete(taskId);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      );
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Task Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Manage your tasks efficiently
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
            <button
              onClick={loadTasks}
              className="mt-2 text-sm text-red-600 hover:underline"
            >
              Retry
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Create Task Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-8">
              <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          </div>

          {/* Task List */}
          <div className="lg:col-span-2">
            <TaskList
              tasks={tasks}
              onUpdate={handleUpdateTask}
              onDelete={handleDeleteTask}
              onToggleComplete={handleToggleComplete}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Key Patterns**:
- Client component for state management
- useEffect for data loading on mount
- 401 redirect to login (auth error handling)
- Real-time UI updates (optimistic updates)
- Loading states with skeleton UI
- Error handling with retry button
- Responsive grid layout (mobile-first)
- Sticky sidebar on desktop

### 5. Landing Page (app/page.tsx)

```typescript
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Evolution of Todo
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            A modern task management application built with Next.js, FastAPI,
            and Better Auth. Secure, fast, and beautiful.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-50 font-semibold border-2 border-blue-600"
            >
              View Dashboard
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Simple & Fast</h3>
            <p className="text-gray-600">
              Create, update, and complete tasks in seconds. Optimized for speed and efficiency.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Secure</h3>
            <p className="text-gray-600">
              JWT authentication with user data isolation. Your tasks are private and secure.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Modern Stack</h3>
            <p className="text-gray-600">
              Built with Next.js 16, FastAPI, SQLModel, and deployed on cloud infrastructure.
            </p>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="mt-20 text-center">
          <h2 className="text-2xl font-semibold mb-8 text-gray-900">
            Powered by Modern Technology
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {["Next.js 16", "React 19", "TypeScript", "Tailwind CSS", "FastAPI", "SQLModel", "PostgreSQL", "Better Auth"].map((tech) => (
              <span
                key={tech}
                className="px-4 py-2 bg-white rounded-full text-sm font-medium text-gray-700 shadow-sm"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Key Patterns**:
- Server Component (no `"use client"`)
- SEO-friendly (static rendering)
- Hero section with CTAs
- Feature highlights
- Tech stack showcase
- Responsive design (mobile-first)
- Tailwind gradient backgrounds

---

## Protected Routes Pattern

### Middleware (middleware.ts)

```typescript
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("auth_token")?.value;

  // Protected routes
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  // Redirect logged-in users away from login
  if (request.nextUrl.pathname === "/login") {
    if (token) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login"],
};
```

---

## Responsive Design Patterns

### Mobile-First Breakpoints
```typescript
// Tailwind config
export default {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px',  // Large desktop
      '2xl': '1536px', // Extra large
    }
  }
}
```

### Responsive Component Example
```typescript
<div className="
  grid
  grid-cols-1           // Mobile: 1 column
  md:grid-cols-2        // Tablet: 2 columns
  lg:grid-cols-3        // Desktop: 3 columns
  gap-4                 // Consistent spacing
">
  {items.map(item => <ItemCard key={item.id} item={item} />)}
</div>
```

---

## Error Handling Patterns

### Global Error Boundary (app/error.tsx)
```typescript
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
        <p className="text-gray-600 mb-4">{error.message}</p>
        <button
          onClick={reset}
          className="px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
```

---

## Performance Optimization

### 1. Code Splitting
```typescript
// Dynamic import for heavy components
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("@/components/HeavyChart"), {
  loading: () => <p>Loading chart...</p>,
  ssr: false, // Disable SSR for client-only components
});
```

### 2. Image Optimization
```typescript
import Image from "next/image";

<Image
  src="/avatar.jpg"
  alt="User avatar"
  width={40}
  height={40}
  className="rounded-full"
  priority // Above-the-fold images
/>
```

### 3. Caching Strategies
```typescript
// app/api/tasks/route.ts
export const revalidate = 60; // Revalidate every 60 seconds

export async function GET() {
  const tasks = await getTasks();
  return Response.json(tasks);
}
```

---

## Testing Patterns (Phase III+)

### Component Tests (Jest + React Testing Library)
```typescript
import { render, screen, fireEvent } from "@testing-library/react";
import TaskItem from "@/components/tasks/TaskItem";

describe("TaskItem", () => {
  const mockTask = {
    id: "1",
    title: "Test Task",
    description: "Test",
    status: "pending" as const,
    created_at: "2026-01-10",
    updated_at: "2026-01-10",
  };

  it("renders task title", () => {
    render(
      <TaskItem
        task={mockTask}
        onUpdate={jest.fn()}
        onDelete={jest.fn()}
        onToggleComplete={jest.fn()}
      />
    );
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("calls onToggleComplete when checkbox clicked", () => {
    const onToggleComplete = jest.fn();
    render(
      <TaskItem
        task={mockTask}
        onUpdate={jest.fn()}
        onDelete={jest.fn()}
        onToggleComplete={onToggleComplete}
      />
    );
    fireEvent.click(screen.getByRole("checkbox"));
    expect(onToggleComplete).toHaveBeenCalledWith("1");
  });
});
```

---

## Future Enhancements (Phase III+)

### 1. Real-time Updates (WebSockets)
```typescript
// lib/websocket.ts
import { io, Socket } from "socket.io-client";

export function useTaskUpdates(onUpdate: (task: Task) => void) {
  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_WS_URL!);

    socket.on("task:updated", onUpdate);

    return () => {
      socket.disconnect();
    };
  }, [onUpdate]);
}
```

### 2. Offline Support (PWA)
```javascript
// next.config.js
const withPWA = require("next-pwa")({
  dest: "public",
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // ... config
});
```

### 3. Advanced Filtering
```typescript
interface TaskFilters {
  status?: TaskStatus;
  search?: string;
  sortBy?: "created_at" | "title" | "updated_at";
  order?: "asc" | "desc";
}

const filteredTasks = useMemo(() => {
  return tasks
    .filter(task => {
      if (filters.status && task.status !== filters.status) return false;
      if (filters.search && !task.title.toLowerCase().includes(filters.search.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      const aVal = a[filters.sortBy || "created_at"];
      const bVal = b[filters.sortBy || "created_at"];
      return filters.order === "desc" ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
    });
}, [tasks, filters]);
```

---

## Deployment Checklist

- [ ] Environment variables configured (.env.local → Vercel)
- [ ] API URL set correctly (production backend)
- [ ] Better Auth configured with production database
- [ ] HTTPS enforced
- [ ] Error tracking setup (Sentry)
- [ ] Analytics setup (Vercel Analytics)
- [ ] SEO meta tags added
- [ ] Favicon and app icons
- [ ] robots.txt and sitemap.xml
- [ ] Performance tested (Lighthouse > 90)

---

## References

- Phase II Implementation: `frontend/app/dashboard/page.tsx`
- API Client: `frontend/lib/api-client.ts`
- Components: `frontend/components/tasks/`
- Types: `frontend/lib/types.ts`

---

**Intelligence Captured**: January 2026
**Ready For**: Phase III (Advanced UI), Phase IV (Real-time), Phase V (Scale)
