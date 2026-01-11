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
 * API response wrapper for loading states
 */
export interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
}
