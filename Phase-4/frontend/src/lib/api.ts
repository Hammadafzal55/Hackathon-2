import { Task, TaskCreate, TaskUpdate } from '../types';
import type { ChatResponse, ConversationListResponse, ConversationDetailResponse } from '../types/chat';

/**
 * Type guard to check if a value is a Task object
 */
export function isTask(value: unknown): value is Task {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as Task).id === 'string' &&
    typeof (value as Task).title === 'string' &&
    typeof (value as Task).status === 'string' &&
    typeof (value as Task).priority === 'number' &&
    typeof (value as Task).user_id === 'string' &&
    typeof (value as Task).created_at === 'string' &&
    typeof (value as Task).updated_at === 'string' &&
    ((value as Task).completed_at === null || typeof (value as Task).completed_at === 'string') &&
    ((value as Task).due_date === undefined || (value as Task).due_date === null || typeof (value as Task).due_date === 'string')
  );
}

/**
 * Type guard to check if a value is a TaskCreate object
 */
export function isTaskCreate(value: unknown): value is TaskCreate {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof (value as TaskCreate).title === 'string' &&
    ((value as TaskCreate).description === undefined || (value as TaskCreate).description === null || typeof (value as TaskCreate).description === 'string') &&
    ((value as TaskCreate).status === undefined || (value as TaskCreate).status === null || typeof (value as TaskCreate).status === 'string') &&
    ((value as TaskCreate).priority === undefined || (value as TaskCreate).priority === null || typeof (value as TaskCreate).priority === 'number') &&
    ((value as TaskCreate).due_date === undefined || (value as TaskCreate).due_date === null || typeof (value as TaskCreate).due_date === 'string')
  );
}

/**
 * Type guard to check if a value is a TaskUpdate object
 */
export function isTaskUpdate(value: unknown): value is TaskUpdate {
  return (
    typeof value === 'object' &&
    value !== null &&
    (
      (value as TaskUpdate).title !== undefined ||
      (value as TaskUpdate).description !== undefined ||
      (value as TaskUpdate).status !== undefined ||
      (value as TaskUpdate).priority !== undefined ||
      (value as TaskUpdate).due_date !== undefined
    )
  );
}

/**
 * Type guard to check if a value is an array of Task objects
 */
export function isTaskArray(value: unknown): value is Task[] {
  return Array.isArray(value) && value.every(item => isTask(item));
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly response: Response;

  constructor(message: string, statusCode: number, response: Response) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

/**
 * Base API client for Todo backend
 */
class ApiClient {
  private readonly baseUrl: string;
  private cachedToken: string | null = null;
  private tokenFetchPromise: Promise<string | null> | null = null;

  constructor() {
    // Use NEXT_PUBLIC_API_URL if available, otherwise default to localhost
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  /**
   * Helper method to get the authenticated user's ID from Better Auth session with timeout
   */
  private async getCurrentUserId(): Promise<string | null> {
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise<null>((_, reject) => {
        setTimeout(() => reject(new Error('Timeout getting user ID')), 5000); // 5 second timeout
      });

      // Get the session which should contain user information
      const { authClient } = await import('./auth');
      const sessionPromise = authClient.getSession();

      // Race the session retrieval with timeout
      const session = await Promise.race([sessionPromise, timeoutPromise]);

      // The session object from better-auth wraps the data in a `data` property.
      const userId = session?.data?.user?.id;

      if (userId) {
        console.log('Retrieved user ID from Better Auth session:', userId);
        return userId;
      } else {
        console.warn('No user ID found in Better Auth session, falling back to JWT token.');
        return await this.getUserIdFromToken();
      }
    } catch (error) {
      console.error('Error getting user ID from session:', error);

      // As a fallback, try to get user ID from the JWT token
      return await this.getUserIdFromToken();
    }
  }

  /**
   * Helper method to get user ID from JWT token as fallback with timeout
   */
  private async getUserIdFromToken(): Promise<string | null> {
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise<null>((_, reject) => {
        setTimeout(() => reject(new Error('Timeout getting JWT token')), 5000); // 5 second timeout
      });

      const { authClient } = await import('./auth');
      const tokenPromise = authClient.token();

      // Race the token retrieval with timeout
      const tokenResponse = await Promise.race([tokenPromise, timeoutPromise]);
      const token = tokenResponse?.data?.token;

      if (!token) {
        console.warn('No JWT token available');
        return null;
      }

      // Decode the JWT token to get user ID
      // Split the token and decode the payload (second part)
      const parts = token.split('.');
      if (parts.length !== 3) {
        console.error('Invalid JWT token format');
        return null;
      }

      try {
        // Decode the payload (second part)
        const payload = JSON.parse(atob(parts[1]));

        // Extract user ID from the token (Better Auth typically uses 'sub' for subject/user ID)
        // Also check for other possible fields Better Auth might use
        const userId = payload.sub || payload.userId || payload.jti || payload.user_id ||
                      (payload.user && typeof payload.user === 'object' ? payload.user.id || payload.user.userId : undefined);

        if (!userId) {
          console.error('No user ID found in JWT token payload. Available keys:', Object.keys(payload));
          console.log('Full payload for debugging:', JSON.stringify(payload, null, 2));
          return null;
        }

        console.log('Extracted user ID from JWT:', userId);
        return userId;
      } catch (decodeError) {
        console.error('Error decoding JWT token:', decodeError);
        return null;
      }
    } catch (error) {
      console.error('Error getting user ID from token:', error);
      return null;
    }
  }

  /**
   * Helper method to get a consistent JWT token across all API calls
   */
  private async getConsistentToken(): Promise<string | null> {
    // If we already have a cached token, return it
    if (this.cachedToken) {
      return this.cachedToken;
    }

    // If there's already a pending token fetch, return that promise
    if (this.tokenFetchPromise) {
      return this.tokenFetchPromise;
    }

    // Create a new promise to fetch the token
    this.tokenFetchPromise = (async () => {
      try {
        const { authClient } = await import('./auth');
        const tokenResponse = await authClient.token();

        if (tokenResponse?.data?.token) {
          const token = tokenResponse.data.token;
          console.log('Using JWT token (first 30 chars):', token.substring(0, 30) + '...');
          this.cachedToken = token;
          return token;
        } else {
          console.warn('No JWT token received from authClient.token():', tokenResponse);
          return null;
        }
      } catch (error) {
        console.warn('Could not get JWT token:', error);
        return null;
      } finally {
        // Clear the pending promise after completion
        this.tokenFetchPromise = null;
      }
    })();

    return this.tokenFetchPromise;
  }

  /**
   * Helper method to create headers with authorization
   */
  private async getHeaders(additionalHeaders?: Record<string, string>): Promise<HeadersInit> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add any additional headers passed in
    if (additionalHeaders) {
      Object.assign(headers, additionalHeaders);
    }

    // Get the consistent JWT token
    const token = await this.getConsistentToken();

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.warn('No JWT token available for API request');
    }

    return headers;
  }

  /**
   * Helper method to handle API responses and errors
   */
  private async handleResponse<T>(response: Response, validator: (data: unknown) => data is T): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text().catch(() => `HTTP Error ${response.status}`);
      throw new ApiError(
        `API Error: ${response.status} - ${errorText}`,
        response.status,
        response
      );
    }

    try {
      const data = await response.json();

      // Validate the response data
      if (!validator(data)) {
        // Log the actual data for debugging purposes
        console.error('API Response validation failed:', data);
        console.error('Expected structure validated by:', validator.name);
        throw new Error('Invalid response format from API: Response does not match expected structure');
      }

      return data;
    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new Error('Invalid JSON response from API');
      }
      throw error;
    }
  }

  /**
   * Fetch all tasks for the authenticated user with timeout and retry
   */
  fetchTasks = async (): Promise<Task[]> => {
    return this.makeRequestWithRetry(async () => {
      const headers = await this.getHeaders();

      // Create a timeout promise for the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      try {
        const response = await fetch(`${this.baseUrl}/api/tasks`, {
          method: 'GET',
          headers,
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        return this.handleResponse(response, isTaskArray);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Create a new task for the authenticated user with timeout and retry
   */
  createTask = async (taskData: TaskCreate): Promise<Task> => {
    return this.makeRequestWithRetry(async () => {
      // Validate that taskData is an object before sending
      if (typeof taskData !== 'object' || taskData === null) {
        throw new Error(`Invalid taskData for create: expected object, got ${typeof taskData}`);
      }

      const headers = await this.getHeaders();

      // Create a timeout promise for the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      try {
        const response = await fetch(`${this.baseUrl}/api/tasks`, {
          method: 'POST',
          headers,
          body: JSON.stringify(taskData),
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        return this.handleResponse(response, isTask);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Update a task for the authenticated user with retry
   */
  updateTask = async (taskId: string, taskData: TaskUpdate): Promise<Task> => {
    return this.makeRequestWithRetry(async () => {
      // Validate that taskData is an object before sending
      if (typeof taskData !== 'object' || taskData === null) {
        throw new Error(`Invalid taskData for update: expected object, got ${typeof taskData}. Task ID: ${taskId}`);
      }

      const headers = await this.getHeaders();

      // Create a timeout promise for the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      try {
        const response = await fetch(`${this.baseUrl}/api/tasks/${taskId}`, {
          method: 'PUT',
          headers,
          body: JSON.stringify(taskData),
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        return this.handleResponse(response, isTask);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Delete a task for the authenticated user
   */
  deleteTask = async (taskId: string): Promise<void> => {
    return this.makeRequestWithRetry(async () => {
      const headers = await this.getHeaders();

      // Create a timeout promise for the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      try {
        const response = await fetch(`${this.baseUrl}/api/tasks/${taskId}`, {
          method: 'DELETE',
          headers,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text().catch(() => `HTTP Error ${response.status}`);
          throw new ApiError(
            `API Error: ${response.status} - ${errorText}`,
            response.status,
            response
          );
        }

        // Successful deletion returns no content
        return;
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Toggle task completion status for the authenticated user
   */
  toggleTaskCompletion = async (taskId: string): Promise<Task> => {
    return this.makeRequestWithRetry(async () => {
      // Validate that taskId is a string (UUID)
      if (typeof taskId !== 'string' || !taskId) {
        throw new Error(`Invalid taskId for toggle completion: expected non-empty string, got ${typeof taskId}`);
      }

      const headers = await this.getHeaders();

      // Create a timeout promise for the fetch request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      try {
        const response = await fetch(`${this.baseUrl}/api/tasks/${taskId}/complete`, {
          method: 'PATCH',
          headers,
          signal: controller.signal
        });

        clearTimeout(timeoutId);
        return this.handleResponse(response, isTask);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Send a chat message and get AI response
   */
  sendChatMessage = async (message: string, conversationId?: string): Promise<ChatResponse> => {
    return this.makeRequestWithRetry(async () => {
      const headers = await this.getHeaders();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s for AI response

      try {
        const body: Record<string, unknown> = { message };
        if (conversationId) body.conversation_id = conversationId;

        const response = await fetch(`${this.baseUrl}/api/chat`, {
          method: 'POST',
          headers,
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text().catch(() => `HTTP Error ${response.status}`);
          throw new ApiError(`API Error: ${response.status} - ${errorText}`, response.status, response);
        }

        return await response.json() as ChatResponse;
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('Request timed out. The AI is taking too long to respond.');
        }
        throw error;
      }
    });
  }

  /**
   * List conversations for the current user
   */
  listConversations = async (limit = 20, offset = 0): Promise<ConversationListResponse> => {
    return this.makeRequestWithRetry(async () => {
      const headers = await this.getHeaders();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      try {
        const response = await fetch(
          `${this.baseUrl}/api/conversations?limit=${limit}&offset=${offset}`,
          { method: 'GET', headers, signal: controller.signal }
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text().catch(() => `HTTP Error ${response.status}`);
          throw new ApiError(`API Error: ${response.status} - ${errorText}`, response.status, response);
        }

        return await response.json() as ConversationListResponse;
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Get conversation detail with messages
   */
  getConversation = async (conversationId: string, limit = 50): Promise<ConversationDetailResponse> => {
    return this.makeRequestWithRetry(async () => {
      const headers = await this.getHeaders();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      try {
        const response = await fetch(
          `${this.baseUrl}/api/conversations/${conversationId}?limit=${limit}`,
          { method: 'GET', headers, signal: controller.signal }
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text().catch(() => `HTTP Error ${response.status}`);
          throw new ApiError(`API Error: ${response.status} - ${errorText}`, response.status, response);
        }

        return await response.json() as ConversationDetailResponse;
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
          throw new Error('API request timed out');
        }
        throw error;
      }
    });
  }

  /**
   * Clear the cached token, typically called on sign out
   */
  public clearCachedToken(): void {
    this.cachedToken = null;
    this.tokenFetchPromise = null;
  }

  /**
   * Global retry wrapper for API requests
   * Automatically retries failed requests once, regardless of error type
   */
  private async makeRequestWithRetry<T>(
    requestFn: () => Promise<T>
  ): Promise<T> {
    try {
      // First attempt
      return await requestFn();
    } catch (error) {
      // If first attempt fails, retry once
      try {
        await new Promise(resolve => setTimeout(resolve, 500)); // Brief delay before retry
        return await requestFn();
      } catch (retryError) {
        // If retry also fails, throw the retry error
        throw retryError;
      }
    }
  }
}

// Export a singleton instance of the API client
export const apiClient = new ApiClient();

// Export individual functions for convenience
export const {
  fetchTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskCompletion
} = apiClient;

// Re-export types for convenience
export type { Task, TaskCreate, TaskUpdate } from '../types';

/**
 * Utility function to determine if a task is completed based on its status
 */
function isTaskCompleted(task: Task): boolean {
  return task.status === 'completed';
}

/**
 * Utility function to convert a task status to a boolean completed value
 */
function taskStatusToCompleted(status: string): boolean {
  return status === 'completed';
}

/**
 * Utility function to convert a boolean completed value to a status string
 */
function completedToTaskStatus(completed: boolean): string {
  return completed ? 'completed' : 'pending';
}

// Export types and utilities
export { isTaskCompleted, taskStatusToCompleted, completedToTaskStatus };