// Error handling infrastructure for the Todo application

export class TodoError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TodoError';
  }
}

export class ValidationError extends TodoError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NetworkError extends TodoError {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ApiError extends TodoError {
  public statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

// Error handling utility functions
export const handleApiError = (error: any): string => {
  if (error instanceof ApiError) {
    return `API Error (${error.statusCode}): ${error.message}`;
  } else if (error instanceof NetworkError) {
    return `Network Error: ${error.message}. Please check your connection.`;
  } else if (error instanceof ValidationError) {
    return `Validation Error: ${error.message}`;
  } else if (error instanceof TodoError) {
    return `Application Error: ${error.message}`;
  } else if (error instanceof TypeError && error.message.includes('fetch')) {
    return 'Network Error: Unable to connect to the server. Please check your connection.';
  } else {
    return `Unexpected Error: ${error.message || 'An unknown error occurred'}`;
  }
};

// Validation utility functions
export const validateTaskData = (taskData: any): string | null => {
  if (!taskData.title || typeof taskData.title !== 'string' || taskData.title.trim().length === 0) {
    return 'Title is required and must be a non-empty string';
  }

  if (taskData.title.length > 255) {
    return 'Title must be 255 characters or less';
  }

  if (taskData.description && typeof taskData.description !== 'string') {
    return 'Description must be a string';
  }

  if (taskData.description && taskData.description.length > 1000) {
    return 'Description must be 1000 characters or less';
  }

  if (taskData.status && !['pending', 'in_progress', 'completed', 'cancelled'].includes(taskData.status)) {
    return 'Status must be one of: pending, in_progress, completed, cancelled';
  }

  if (taskData.priority && (typeof taskData.priority !== 'number' || taskData.priority < 1 || taskData.priority > 5)) {
    return 'Priority must be a number between 1 and 5';
  }

  if (taskData.due_date && taskData.due_date !== null) {
    const date = new Date(taskData.due_date);
    if (isNaN(date.getTime())) {
      return 'Due date must be a valid date';
    }
  }

  return null;
};

// Error boundary component interface
export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export const getInitialErrorState = (): ErrorBoundaryState => ({
  hasError: false,
  error: null,
});