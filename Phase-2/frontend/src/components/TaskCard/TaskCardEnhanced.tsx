import React, { useState } from 'react';
import { Task } from '../../types';

interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdate: (updatedTask: Partial<Task>) => void;
}

const TaskCardEnhanced: React.FC<TaskCardProps> = ({ task, onToggle, onDelete, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [editPriority, setEditPriority] = useState(task.priority.toString());

  const handleToggle = () => onToggle(task.id);
  const handleDelete = () => onDelete(task.id);

  const handleSave = () => {
    onUpdate({
      title: editTitle,
      description: editDescription,
      priority: parseInt(editPriority),
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority.toString());
    setIsEditing(false);
  };

  // Convert numeric priority to text
  const getPriorityText = (priority: number): string => {
    switch(priority) {
      case 1: return 'low';
      case 2: return 'medium';
      case 3: return 'high';
      default: return 'medium';
    }
  };

  // Get priority text for current task
  const priorityText = getPriorityText(task.priority);

  // Get priority text for editing
  const editingPriorityText = getPriorityText(parseInt(editPriority));

  // Determine priority color
  const priorityColors = {
    low: 'border-l-green-500 bg-green-50/30 dark:bg-green-900/20',
    medium: 'border-l-yellow-500 bg-yellow-50/30 dark:bg-yellow-900/20',
    high: 'border-l-red-500 bg-red-50/30 dark:bg-red-900/20',
  };

  // Format date if it exists
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (isEditing) {
    return (
      <div className={`glass rounded-xl border-l-4 border border-white/20 backdrop-blur-sm p-5 mb-4 transition-all duration-300 hover:shadow-lg hover:scale-[1.02] ${priorityColors[editingPriorityText as keyof typeof priorityColors]}`}>
        <div className="space-y-4">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-2 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white"
            placeholder="Task title"
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-3 py-2 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white"
            placeholder="Task description"
            rows={3}
          />
          <select
            value={editPriority}
            onChange={(e) => setEditPriority(e.target.value)}
            className="px-3 py-2 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white"
          >
            <option value="1" className="bg-white dark:bg-gray-800">1 (Low)</option>
            <option value="2" className="bg-white dark:bg-gray-800">2 (Medium)</option>
            <option value="3" className="bg-white dark:bg-gray-800">3 (High)</option>
          </select>
          <div className="flex space-x-2 justify-end">
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`glass rounded-xl border-l-4 border border-white/20 backdrop-blur-sm p-5 mb-4 transition-all duration-300 hover:shadow-lg hover:scale-[1.02] ${priorityColors[priorityText as keyof typeof priorityColors]}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={task.status === 'completed'}
            onChange={handleToggle}
            className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-medium truncate ${task.status === 'completed' ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'}`}>
              {task.title}
            </h3>
            {task.description && (
              <p className="mt-1 text-gray-600 dark:text-gray-300 text-sm line-clamp-2">
                {task.description}
              </p>
            )}
            <div className="mt-2 flex flex-wrap gap-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                priorityText === 'low'
                  ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-200'
                  : priorityText === 'medium'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/30 dark:text-yellow-200'
                    : priorityText === 'high'
                      ? 'bg-red-100 text-red-800 dark:bg-red-800/30 dark:text-red-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-800/30 dark:text-red-200'
              }`}>
                {priorityText} priority
              </span>
              {task.due_date && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-800/30 dark:text-blue-200">
                  Due: {formatDate(task.due_date)}
                </span>
              )}
              {task.status === 'completed' && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-200">
                  Completed
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex space-x-2 ml-4">
          <button
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center p-2 text-gray-500 hover:text-blue-500 dark:text-gray-400 dark:hover:text-blue-400 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors duration-200"
            aria-label="Edit task"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={handleDelete}
            className="inline-flex items-center p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-200"
            aria-label="Delete task"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskCardEnhanced;