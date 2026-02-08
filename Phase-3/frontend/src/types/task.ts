/**
 * Represents a task in the Todo application
 */
export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: string; // pending, in_progress, completed, cancelled
  priority: number; // 1-5 scale, 1 being lowest priority
  due_date?: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

/**
 * Interface for creating a new task
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: string; // pending, in_progress, completed, cancelled
  priority?: number; // 1-5 scale, 1 being lowest priority
  due_date?: string | null;
}

/**
 * Interface for updating an existing task
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: string; // pending, in_progress, completed, cancelled
  priority?: number; // 1-5 scale, 1 being lowest priority
  due_date?: string | null;
}