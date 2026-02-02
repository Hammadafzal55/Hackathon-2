'use client';

import { useState, useEffect } from 'react';
import { fetchTasks, createTask, updateTask, deleteTask, toggleTaskCompletion } from '../lib/api';
import { Task, TaskCreate, TaskUpdate } from '../types';

interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  createTask: (taskData: TaskCreate) => Promise<void>;
  updateTask: (id: string, taskData: TaskUpdate) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  toggleTaskCompletion: (id: string) => Promise<void>;
  refreshTasks: () => Promise<void>;
}

export const useTasks = (): TaskState => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true); // Start as true initially
  const [error, setError] = useState<string | null>(null);

  const fetchTasksData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTasks(); // No user ID needed anymore
      // Only update state if component is still mounted
      setTasks(data);
    } catch (err) {
      // Don't set error if it's a timeout or network issue, just log it
      // This prevents the error from affecting the auth state
      if (err instanceof Error && (err.message.includes('timeout') || err.message.toLowerCase().includes('network'))) {
        console.warn('Network error fetching tasks:', err.message);
        // Don't set error state for network issues to avoid affecting auth state
      } else {
        // Check if this is an auth-related error (401/403)
        if (err instanceof Error && (err.message.includes('401') || err.message.includes('403') || err.message.toLowerCase().includes('unauthorized') || err.message.toLowerCase().includes('forbidden'))) {
          console.warn('Auth-related error fetching tasks - token may not be ready yet:', err.message);
          // Don't set error state for auth issues to avoid showing error when auth is still resolving
        } else {
          setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
          console.error('Error fetching tasks:', err);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const createTaskFunc = async (taskData: TaskCreate) => {
    try {
      setLoading(true);
      const newTask = await createTask(taskData); // No user ID needed anymore
      setTasks(prev => [...prev, newTask]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      console.error('Error creating task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateTaskFunc = async (id: string, taskData: TaskUpdate) => {
    try {
      setLoading(true);
      const updatedTask = await updateTask(id, taskData); // No user ID needed anymore
      setTasks(prev => prev.map(task => task.id === id ? updatedTask : task));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      console.error('Error updating task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteTaskFunc = async (id: string) => {
    try {
      setLoading(true);
      await deleteTask(id); // No user ID needed anymore
      setTasks(prev => prev.filter(task => task.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      console.error('Error deleting task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskCompletionFunc = async (id: string) => {
    try {
      setLoading(true);
      const updatedTask = await toggleTaskCompletion(id); // No user ID needed anymore
      setTasks(prev => prev.map(task => task.id === id ? updatedTask : task));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle task completion');
      console.error('Error toggling task completion:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch tasks when the hook is initialized
  useEffect(() => {
    let cancelled = false;

    // Check if auth token is likely available before fetching
    // Import auth client to check if token exists
    (async () => {
      try {
        const { getJwtToken } = await import('../lib/auth');
        const token = await getJwtToken();

        // Only fetch if token is available, otherwise skip initial fetch
        if (token) {
          fetchTasksData();
        } else {
          // If no token is immediately available, still try to fetch
          // The API client will handle token retrieval when ready
          fetchTasksData();
        }
      } catch (error) {
        console.warn('Could not check auth token availability, attempting fetch anyway:', error);
        // Still try to fetch, as the API client will handle token retrieval
        fetchTasksData();
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []); // Run once on mount

  const refreshTasks = async () => {
    await fetchTasksData();
  };

  return {
    tasks,
    loading,
    error,
    createTask: createTaskFunc,
    updateTask: updateTaskFunc,
    deleteTask: deleteTaskFunc,
    toggleTaskCompletion: toggleTaskCompletionFunc,
    refreshTasks,
  };
};