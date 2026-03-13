'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../lib/api';
import { Task, TaskCreate, TaskUpdate } from '../types';

export interface SearchFilterSort {
  search?: string;
  status?: string;
  priority?: string;
  tags?: string;
  due_before?: string;
  due_after?: string;
  sort_by?: string;
  sort_dir?: string;
}

interface TaskState {
  tasks: Task[];
  totalCount: number;
  loading: boolean;
  error: string | null;
  createTask: (taskData: TaskCreate) => Promise<void>;
  updateTask: (id: string, taskData: TaskUpdate) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  toggleTaskCompletion: (id: string) => Promise<void>;
  refreshTasks: () => Promise<void>;
}

export const useTasks = (params?: SearchFilterSort): TaskState => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasksData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.fetchTasks(params);
      setTasks(data.tasks);
      setTotalCount(data.total_count);
    } catch (err) {
      if (err instanceof Error && (err.message.includes('timeout') || err.message.toLowerCase().includes('network'))) {
        console.warn('Network error fetching tasks:', err.message);
      } else if (err instanceof Error && (err.message.includes('401') || err.message.includes('403'))) {
        console.warn('Auth error fetching tasks:', err.message);
      } else {
        setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
        console.error('Error fetching tasks:', err);
      }
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(params)]);

  const createTaskFunc = async (taskData: TaskCreate) => {
    try {
      setLoading(true);
      const newTask = await apiClient.createTask(taskData);
      setTasks(prev => [newTask, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateTaskFunc = async (id: string, taskData: TaskUpdate) => {
    try {
      setLoading(true);
      const updatedTask = await apiClient.updateTask(id, taskData);
      setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteTaskFunc = async (id: string) => {
    try {
      setLoading(true);
      await apiClient.deleteTask(id);
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskCompletionFunc = async (id: string) => {
    try {
      setLoading(true);
      const updatedTask = await apiClient.toggleTaskCompletion(id);
      setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle task completion');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasksData();
  }, [fetchTasksData]);

  return {
    tasks,
    totalCount,
    loading,
    error,
    createTask: createTaskFunc,
    updateTask: updateTaskFunc,
    deleteTask: deleteTaskFunc,
    toggleTaskCompletion: toggleTaskCompletionFunc,
    refreshTasks: fetchTasksData,
  };
};
