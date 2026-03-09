'use client';

import React, { useState } from 'react';
import { TaskCreate } from '../types/task';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => Promise<void>;
  onCancel?: () => void;
  submitButtonText?: string;
  initialData?: Partial<TaskCreate>;
  isSubmitting?: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  onCancel,
  submitButtonText = 'Add Task',
  initialData = {},
  isSubmitting = false
}) => {
  const [title, setTitle] = useState(initialData.title || '');
  const [description, setDescription] = useState(initialData.description || '');
  const [priority, setPriority] = useState<number>(initialData.priority || 1);
  const [status, setStatus] = useState(initialData.status || 'pending');
  const [dueDate, setDueDate] = useState(initialData.due_date || '');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 255) {
      newErrors.title = 'Title must be 255 characters or less';
    }

    if (description && description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const taskData: TaskCreate = {
      title: title.trim(),
      description: description.trim() || null,
      priority,
      status,
      due_date: dueDate || null,
    };

    try {
      await onSubmit(taskData);
      // Reset form after successful submission
      if (!initialData.title) {  // Only reset if it's a new task, not an edit
        setTitle('');
        setDescription('');
        setPriority(1);
        setStatus('pending');
        setDueDate('');
        setErrors({});
      }
    } catch (error) {
      console.error('Error submitting task:', error);
    }
  };

  return (
    <div className="task-form">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="form-group">
          <label htmlFor="title" className="form-label">
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={`form-input ${errors.title ? 'border-red-500' : ''}`}
            placeholder="Enter task title"
          />
          {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
        </div>

        <div className="form-group">
          <label htmlFor="description" className="form-label">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="form-textarea"
            rows={3}
            placeholder="Enter task description (optional)"
          />
          {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="form-group">
            <label htmlFor="priority" className="form-label">
              Priority
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="form-input"
            >
              <option value={1}>Low</option>
              <option value={2}>Medium</option>
              <option value={3}>High</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="status" className="form-label">
              Status
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="form-input"
            >
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="dueDate" className="form-label">
            Due Date
          </label>
          <input
            type="date"
            id="dueDate"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="form-input"
          />
        </div>

        <div className="flex space-x-3 pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className={`btn btn-primary ${isSubmitting ? 'opacity-75 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? (
              <>
                <span className="loading-spinner"></span>
                <span className="ml-2">Saving...</span>
              </>
            ) : (
              submitButtonText
            )}
          </button>

          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-outline"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default TaskForm;