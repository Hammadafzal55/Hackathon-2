import React, { useState } from 'react';
import { TaskCreate } from '../../types';
import { TagInput } from '../Tasks/TagInput';
import { RecurrenceForm } from '../Tasks/RecurrenceForm';
import type { RecurrenceRule } from '../../types/task';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => void;
  submitButtonText?: string;
}

const REMINDER_OPTIONS = [
  { label: '15 min before', value: 15 },
  { label: '1 hour before', value: 60 },
  { label: '3 hours before', value: 180 },
  { label: '1 day before', value: 1440 },
  { label: '2 days before', value: 2880 },
];

const TaskForm: React.FC<TaskFormProps> = ({ onSubmit, submitButtonText = 'Add Task' }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<number>(2);
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [recurrenceRule, setRecurrenceRule] = useState<RecurrenceRule | null>(null);
  const [selectedReminders, setSelectedReminders] = useState<number[]>([]);

  const handleReminderToggle = (minutes: number) => {
    setSelectedReminders(prev =>
      prev.includes(minutes) ? prev.filter(m => m !== minutes) : [...prev, minutes]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const taskData: TaskCreate = {
      title,
      description: description || null,
      priority,
      due_date: dueDate || null,
      tags,
      recurrence_rule: recurrenceRule,
      reminders: dueDate && selectedReminders.length > 0
        ? selectedReminders.map(m => ({ lead_time_minutes: m }))
        : [],
    };

    onSubmit(taskData);

    // Reset form
    setTitle('');
    setDescription('');
    setPriority(2);
    setDueDate('');
    setTags([]);
    setRecurrenceRule(null);
    setSelectedReminders([]);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title + Priority row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Task Title *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full px-4 py-3 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            placeholder="What needs to be done?"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            className="w-full px-4 py-3 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white"
          >
            <option value={1} className="bg-white dark:bg-gray-800">1 – Low</option>
            <option value={2} className="bg-white dark:bg-gray-800">2 – Medium</option>
            <option value={3} className="bg-white dark:bg-gray-800">3 – High</option>
            <option value={4} className="bg-white dark:bg-gray-800">4 – Very High</option>
            <option value={5} className="bg-white dark:bg-gray-800">5 – Critical</option>
          </select>
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="w-full px-4 py-3 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
          placeholder="Add details about this task..."
        />
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tags</label>
        <TagInput value={tags} onChange={setTags} />
      </div>

      {/* Due Date + Reminders */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Due Date (optional)
          </label>
          <input
            type="date"
            id="dueDate"
            value={dueDate}
            onChange={(e) => { setDueDate(e.target.value); if (!e.target.value) setSelectedReminders([]); }}
            className="w-full px-4 py-3 bg-white/20 dark:bg-gray-800/30 border border-white/30 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 text-gray-900 dark:text-white"
          />
        </div>

        {dueDate && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Reminders
            </label>
            <div className="flex flex-wrap gap-2">
              {REMINDER_OPTIONS.map(({ label, value }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => handleReminderToggle(value)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    selectedReminders.includes(value)
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white/10 text-gray-700 dark:text-gray-300 border-white/30 hover:border-blue-400'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recurrence */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Recurrence</label>
        <RecurrenceForm value={recurrenceRule} onChange={setRecurrenceRule} />
      </div>

      {/* Submit */}
      <div className="flex justify-end">
        <button
          type="submit"
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium rounded-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-transparent"
        >
          {submitButtonText}
        </button>
      </div>
    </form>
  );
};

export default TaskForm;
