export interface RecurrenceRule {
  pattern: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  end_condition: 'never' | 'after_n' | 'by_date';
  end_after_n?: number | null;
  end_by_date?: string | null;
}

export interface ReminderRead {
  id: string;
  task_id: string;
  lead_time_minutes: number;
  fire_at: string;
  status: string;
  created_at: string;
}

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
  tags: string[];
  recurrence_rule?: RecurrenceRule | null;
  recurrence_parent_id?: string | null;
  next_occurrence?: string | null;
  reminders?: ReminderRead[];
}

/**
 * Interface for creating a new task
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: string;
  priority?: number;
  due_date?: string | null;
  tags?: string[];
  recurrence_rule?: RecurrenceRule | null;
  reminders?: Array<{ lead_time_minutes: number }>;
}

/**
 * Interface for updating an existing task
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: string;
  priority?: number;
  due_date?: string | null;
  tags?: string[];
  recurrence_rule?: RecurrenceRule | null;
  reminders?: Array<{ lead_time_minutes: number }>;
}
