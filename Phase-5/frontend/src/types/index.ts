/**
 * TypeScript interfaces for Task model that match the backend data structure
 */

// Define UUID type alias for better type safety
type UUID = string;

/**
 * Interface representing a complete Task entity from the backend
 */
export interface Task {
  id: UUID;
  title: string;
  description: string | null;
  status: string;           // Status: "pending", "in_progress", "completed", "cancelled"
  priority: number;         // Priority level 1-5 (1 being lowest)
  user_id: UUID;
  created_at: string;
  updated_at: string;
  completed_at: string | null;  // Timestamp when task was completed, null if not completed
  due_date?: string | null;     // Optional due date
}

/**
 * Interface for creating a new Task
 * All fields except title are optional with default values handled by backend
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: string;        // Optional status: "pending", "in_progress", "completed", "cancelled" - defaults to "pending"
  priority?: number;      // Optional priority 1-5, defaults to 1
  due_date?: string | null; // Optional due date
}

/**
 * Interface for updating an existing Task
 * All fields are optional to allow partial updates
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: string;              // Status: "pending", "in_progress", "completed", "cancelled"
  priority?: number;            // Priority level 1-5
  due_date?: string | null;     // Optional due date
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  error: string;
  message?: string;
  statusCode: number;
}

/**
 * Possible HTTP methods for API requests
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Common API request options
 */
export interface ApiRequestOptions {
  headers?: Record<string, string>;
  signal?: AbortSignal;
}