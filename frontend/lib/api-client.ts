/**
 * API Client for Todo Backend
 * Handles all HTTP communication with authentication
 */

import type { Task, TaskCreate, TaskUpdate, ApiError, SignupRequest, LoginRequest, AuthResponse, ChatRequest, ChatResponse, ChatHealthResponse } from "./types";

/**
 * Base API URL from environment
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get JWT token from session/storage
 * TODO: Implement with Better Auth
 */
async function getAuthToken(): Promise<string | null> {
  // This will be replaced with Better Auth session management
  // For now, check localStorage (development only)
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token");
  }
  return null;
}

/**
 * Custom error class for API errors
 */
export class ApiClientError extends Error {
  constructor(
    public statusCode: number,
    public apiError: ApiError
  ) {
    super(
      typeof apiError.detail === "string"
        ? apiError.detail
        : "Validation error"
    );
    this.name = "ApiClientError";
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    if (typeof this.apiError.detail === "string") {
      return this.apiError.detail;
    }

    // Multiple validation errors
    const errors = this.apiError.detail;
    if (errors.length === 1) {
      return errors[0].message;
    }

    return `${errors.length} validation errors occurred`;
  }

  /**
   * Get all validation errors
   */
  getValidationErrors() {
    if (typeof this.apiError.detail === "string") {
      return [];
    }
    return this.apiError.detail;
  }
}

/**
 * Make authenticated API request
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  // Parse JSON response
  const data = await response.json();

  // Handle error responses
  if (!response.ok) {
    throw new ApiClientError(response.status, data as ApiError);
  }

  return data as T;
}

/**
 * API Client with all backend endpoints
 */
export const apiClient = {
  /**
   * Health check endpoint
   */
  async health(): Promise<{ status: string; message: string; version: string }> {
    return fetchWithAuth("/");
  },

  /**
   * Task management endpoints
   */
  tasks: {
    /**
     * List all tasks for authenticated user
     */
    async list(): Promise<Task[]> {
      return fetchWithAuth<Task[]>("/api/tasks");
    },

    /**
     * Get specific task by ID
     */
    async get(taskId: string): Promise<Task> {
      return fetchWithAuth<Task>(`/api/tasks/${taskId}`);
    },

    /**
     * Create new task
     */
    async create(data: TaskCreate): Promise<Task> {
      return fetchWithAuth<Task>("/api/tasks", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    /**
     * Update existing task
     */
    async update(taskId: string, data: TaskUpdate): Promise<Task> {
      return fetchWithAuth<Task>(`/api/tasks/${taskId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
    },

    /**
     * Delete task
     */
    async delete(taskId: string): Promise<void> {
      return fetchWithAuth<void>(`/api/tasks/${taskId}`, {
        method: "DELETE",
      });
    },

    /**
     * Mark task as completed
     */
    async markComplete(taskId: string): Promise<Task> {
      return fetchWithAuth<Task>(`/api/tasks/${taskId}/complete`, {
        method: "PATCH",
      });
    },
  },

  /**
   * Authentication endpoints
   */
  auth: {
    /**
     * Sign up with email and password
     */
    async signup(data: SignupRequest): Promise<AuthResponse> {
      // For signup, we don't need auth token
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: "POST",
        headers,
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new ApiClientError(response.status, result as ApiError);
      }

      return result as AuthResponse;
    },

    /**
     * Login with email and password
     */
    async login(data: LoginRequest): Promise<AuthResponse> {
      // For login, we don't need auth token
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers,
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new ApiClientError(response.status, result as ApiError);
      }

      return result as AuthResponse;
    },
  },

  /**
   * Chat endpoints (Phase III: AI Chatbot)
   */
  chat: {
    /**
     * Send a message to the AI chatbot
     */
    async send(data: ChatRequest): Promise<ChatResponse> {
      return fetchWithAuth<ChatResponse>("/api/chat", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    /**
     * Check chat service health
     */
    async health(): Promise<ChatHealthResponse> {
      return fetchWithAuth<ChatHealthResponse>("/api/chat/health");
    },
  },
};

/**
 * Hook-friendly API client functions
 * These can be used directly in React components
 */

export async function getTasks(): Promise<Task[]> {
  return apiClient.tasks.list();
}

export async function getTask(taskId: string): Promise<Task> {
  return apiClient.tasks.get(taskId);
}

export async function createTask(data: TaskCreate): Promise<Task> {
  return apiClient.tasks.create(data);
}

export async function updateTask(
  taskId: string,
  data: TaskUpdate
): Promise<Task> {
  return apiClient.tasks.update(taskId, data);
}

export async function deleteTask(taskId: string): Promise<void> {
  return apiClient.tasks.delete(taskId);
}

export async function markTaskComplete(taskId: string): Promise<Task> {
  return apiClient.tasks.markComplete(taskId);
}

/**
 * Authentication hook-friendly functions
 */
export async function signup(data: SignupRequest): Promise<AuthResponse> {
  return apiClient.auth.signup(data);
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  return apiClient.auth.login(data);
}

/**
 * Temporary auth helper (will be replaced with Better Auth)
 */
export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

export function clearAuthToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

/**
 * Chat hook-friendly functions
 */
export async function sendChatMessage(data: ChatRequest): Promise<ChatResponse> {
  return apiClient.chat.send(data);
}

export async function getChatHealth(): Promise<ChatHealthResponse> {
  return apiClient.chat.health();
}
