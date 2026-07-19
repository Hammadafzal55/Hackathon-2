/**
 * TypeScript interfaces for Task model that match the backend data structure
 */

// Define UUID type alias for better type safety
type UUID = string;

/**
 * Recurrence rule for recurring tasks
 */
export interface RecurrenceRule {
  pattern: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  end_condition: 'never' | 'after_n' | 'by_date';
  end_after_n?: number | null;
  end_by_date?: string | null;
}

/**
 * Reminder configuration for tasks
 */
export interface ReminderRead {
  id: string;
  task_id: string;
  lead_time_minutes: number;
  fire_at: string;
  status: string;
  created_at: string;
}

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
  tags: string[];               // Task tags/labels
  recurrence_rule?: RecurrenceRule | null;  // Optional recurrence configuration
  recurrence_parent_id?: string | null;     // Parent task ID if this is a recurring instance
  next_occurrence?: string | null;          // Next occurrence date for recurring tasks
  reminders?: ReminderRead[];    // Task reminders
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
  tags?: string[];        // Optional tags
  recurrence_rule?: RecurrenceRule | null;  // Optional recurrence configuration
  reminders?: Array<{ lead_time_minutes: number }>;  // Optional reminders
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
  tags?: string[];              // Optional tags
  recurrence_rule?: RecurrenceRule | null;  // Optional recurrence configuration
  reminders?: Array<{ lead_time_minutes: number }>;  // Optional reminders
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
