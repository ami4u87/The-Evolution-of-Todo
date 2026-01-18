/**
 * Type definitions for Todo application
 * Matches backend API schemas
 */

/**
 * Task status type - must match backend validation
 */
export type TaskStatus = "pending" | "completed";

/**
 * Complete task object as returned by API
 */
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * Task creation request body
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
}

/**
 * Task update request body (all fields optional)
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
}

/**
 * API error response format
 */
export interface ApiError {
  detail: string | ApiValidationError[];
}

/**
 * Validation error format
 */
export interface ApiValidationError {
  field: string;
  message: string;
}

/**
 * User session data
 */
export interface User {
  id: string;
  email: string;
}

/**
 * Authentication request types
 */
export interface SignupRequest {
  email: string;
  password: string;
  password_confirm: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user_id: string;
  email: string;
}

/**
 * API response wrapper for loading states
 */
export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
}

/**
 * Chat types for AI chatbot
 */
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ToolAction {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown> | string | null;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  actions_taken: ToolAction[];
}

export interface ChatHealthResponse {
  status: "available" | "unavailable";
  model: string | null;
}
