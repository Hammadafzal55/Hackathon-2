import React, { useState } from 'react';
import { Task } from '../../types';

interface TaskCardProps {
  task: Task;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onUpdate: (updatedTask: Partial<Task>) => void;
}

// Priority badge config (1-5 scale)
const PRIORITY_CONFIG: Record<number, { label: string; badge: string; border: string }> = {
  1: { label: 'Low', badge: 'bg-gray-100 text-gray-600 dark:bg-gray-700/50 dark:text-gray-300', border: 'border-l-gray-400' },
  2: { label: 'Medium', badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300', border: 'border-l-blue-500' },
  3: { label: 'High', badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300', border: 'border-l-amber-500' },
  4: { label: 'Very High', badge: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300', border: 'border-l-orange-500' },
  5: { label: 'Critical', badge: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300', border: 'border-l-red-500' },
};

function getDueDateColor(dueDateStr: string | null | undefined): string {
  if (!dueDateStr) return 'text-gray-400';
  const due = new Date(dueDateStr);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const dueDay = new Date(due.getFullYear(), due.getMonth(), due.getDate());
  const diffMs = dueDay.getTime() - today.getTime();
  const diffDays = Math.round(diffMs / 86400000);
  if (diffDays < 0) return 'text-red-400';
  if (diffDays === 0) return 'text-orange-400';
  if (diffDays === 1) return 'text-amber-400';
  if (diffDays <= 7) return 'text-yellow-400';
  return 'text-gray-400';
}

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

const TaskCardEnhanced: React.FC<TaskCardProps> = ({ task, onToggle, onDelete, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [editPriority, setEditPriority] = useState(task.priority.toString());

  const priorityCfg = PRIORITY_CONFIG[task.priority] || PRIORITY_CONFIG[2];
  const dueDateColor = getDueDateColor(task.due_date);

  const handleSave = () => {
    onUpdate({ title: editTitle, description: editDescription, priority: parseInt(editPriority) });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority.toString());
    setIsEditing(false);
  };

  const visibleTags = task.tags?.slice(0, 3) ?? [];
  const extraTagCount = (task.tags?.length ?? 0) - 3;

  if (isEditing) {
    const editCfg = PRIORITY_CONFIG[parseInt(editPriority)] || PRIORITY_CONFIG[2];
    return (
      <div className={`glass rounded-xl border-l-4 border border-white/20 backdrop-blur-sm p-5 mb-4 transition-all duration-300 hover:shadow-lg ${editCfg.border}`}>
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
            <option value="1" className="bg-white dark:bg-gray-800">1 – Low</option>
            <option value="2" className="bg-white dark:bg-gray-800">2 – Medium</option>
            <option value="3" className="bg-white dark:bg-gray-800">3 – High</option>
            <option value="4" className="bg-white dark:bg-gray-800">4 – Very High</option>
            <option value="5" className="bg-white dark:bg-gray-800">5 – Critical</option>
          </select>
          <div className="flex space-x-2 justify-end">
            <button onClick={handleCancel} className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">Cancel</button>
            <button onClick={handleSave} className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">Save</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`glass rounded-xl border-l-4 border border-white/20 backdrop-blur-sm p-5 mb-4 transition-all duration-300 hover:shadow-lg hover:scale-[1.01] ${priorityCfg.border}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={task.status === 'completed'}
            onChange={() => onToggle(task.id)}
            className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className={`text-lg font-medium truncate ${task.status === 'completed' ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'}`}>
                {task.title}
              </h3>
              {task.recurrence_rule && (
                <span title="Recurring task" className="text-blue-400 text-sm flex-shrink-0">🔄</span>
              )}
            </div>

            {task.description && (
              <p className="mt-1 text-gray-600 dark:text-gray-300 text-sm line-clamp-2">{task.description}</p>
            )}

            <div className="mt-2 flex flex-wrap gap-2 items-center">
              {/* Priority badge */}
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${priorityCfg.badge}`}>
                P{task.priority} {priorityCfg.label}
              </span>

              {/* Due date */}
              {task.due_date && (
                <span className={`inline-flex items-center gap-1 text-xs font-medium ${dueDateColor}`}>
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {formatDate(task.due_date)}
                </span>
              )}

              {/* Completed badge */}
              {task.status === 'completed' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                  Completed
                </span>
              )}

              {/* Tag chips */}
              {visibleTags.map(tag => (
                <span key={tag} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                  #{tag}
                </span>
              ))}
              {extraTagCount > 0 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500 dark:bg-gray-800/50 dark:text-gray-400">
                  +{extraTagCount} more
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex space-x-1 ml-3">
          <button
            onClick={() => setIsEditing(true)}
            className="p-2 text-gray-500 hover:text-blue-500 dark:text-gray-400 dark:hover:text-blue-400 rounded-full hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
            aria-label="Edit task"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="p-2 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            aria-label="Delete task"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskCardEnhanced;
