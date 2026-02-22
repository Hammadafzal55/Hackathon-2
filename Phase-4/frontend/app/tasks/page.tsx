'use client';

import React, { useState } from 'react';
import { useTasks } from '../../src/hooks/useTasks';
import { useAuth } from '@/src/providers/AuthProvider';
import TaskList from '../../src/components/TaskList';
import TaskForm from '../../src/components/TaskForm/TaskForm';
import { TaskCreate } from '../../src/types';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TasksPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  // Controlled redirect using useEffect with dependency array to ensure it only runs when values change
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace('/auth/login');
    }
  }, [authLoading, user, router]);

  // Initialize useTasks hook - authentication is handled by the backend via JWT
  const {
    tasks,
    loading: tasksLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
    refreshTasks
  } = useTasks();

  const [showTaskForm, setShowTaskForm] = useState(false);

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Don't render the page if user is not authenticated
  if (!user && !authLoading) {
    return null;
  }

  // At this point, user !== null (authenticated)
  // Continue to render the page normally

  const handleCreateTask = async (taskData: TaskCreate) => {
    try {
      await createTask(taskData);
      // Optionally show success notification
      setShowTaskForm(false); // Hide form after successful submission
    } catch (err) {
      console.error('Failed to create task:', err);
      // Optionally show error notification
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white sm:text-5xl">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                My Tasks
              </span>
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">
              Manage your tasks efficiently
            </p>
          </div>
          <button
            onClick={() => setShowTaskForm(!showTaskForm)}
            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium rounded-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-transparent"
          >
            {showTaskForm ? 'Cancel' : 'Add Task'}
          </button>
        </div>

        {showTaskForm && (
          <div className="glass rounded-2xl p-6 border border-white/20 backdrop-blur-sm mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">Create New Task</h2>
              <p className="text-gray-600 dark:text-gray-400">Add a new task to your list</p>
            </div>
            <TaskForm
              onSubmit={handleCreateTask}
              submitButtonText="Add New Task"
            />

            {error && (
              <div className="notification notification-error mt-6">
                <p className="font-medium">Error:</p>
                <p>{error}</p>
              </div>
            )}
          </div>
        )}

        <div className="glass rounded-2xl p-6 border border-white/20 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Your Tasks</h2>
            <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-medium px-3 py-1 rounded-full">
              {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
            </span>
          </div>

          <TaskList
            tasks={tasks}
            loading={tasksLoading}
            error={error}
            onTaskToggle={toggleTaskCompletion}
            onTaskDelete={deleteTask}
            onTaskUpdate={updateTask}
            emptyMessage="No tasks yet. Add a new task to get started!"
          />
        </div>

        <div className="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>Your tasks are securely stored and synchronized in real-time</p>
        </div>
      </div>
    </div>
  );
}