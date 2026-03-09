'use client';

import React from 'react';
import { Task } from '../types/task';
import TaskItem from './TaskItem';
import { SearchBar } from './Tasks/SearchBar';
import { FilterPanel, FilterState } from './Tasks/FilterPanel';
import { SortControl } from './Tasks/SortControl';
import type { SearchFilterSort } from '../hooks/useTasks';

interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  error?: string | null;
  onTaskToggle: (id: string) => void;
  onTaskDelete: (id: string) => void;
  onTaskUpdate: (id: string, task: Partial<Task>) => void;
  emptyMessage?: string;
  // Search/filter/sort props (optional - TaskList works standalone too)
  filterParams?: SearchFilterSort;
  onFilterChange?: (params: SearchFilterSort) => void;
  totalCount?: number;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  loading = false,
  error,
  onTaskToggle,
  onTaskDelete,
  onTaskUpdate,
  emptyMessage = 'No tasks found. Add a new task to get started!',
  filterParams,
  onFilterChange,
  totalCount,
}) => {
  const hasFilterBar = !!onFilterChange;

  const handleSearch = (search: string) => {
    if (!onFilterChange) return;
    onFilterChange({ ...filterParams, search: search || undefined });
  };

  const handleFilterChange = (filters: FilterState) => {
    if (!onFilterChange) return;
    onFilterChange({
      ...filterParams,
      status: filters.status.join(',') || undefined,
      priority: filters.priority.join(',') || undefined,
      tags: filters.tags.join(',') || undefined,
      due_before: filters.due_before || undefined,
      due_after: filters.due_after || undefined,
    });
  };

  const handleSortChange = (sort_by: string, sort_dir: string) => {
    if (!onFilterChange) return;
    onFilterChange({ ...filterParams, sort_by, sort_dir });
  };

  // Convert comma-separated string params to FilterState arrays
  const currentFilters: FilterState = {
    status: filterParams?.status ? filterParams.status.split(',').filter(Boolean) : [],
    priority: filterParams?.priority ? filterParams.priority.split(',').filter(Boolean) : [],
    tags: filterParams?.tags ? filterParams.tags.split(',').filter(Boolean) : [],
    due_before: filterParams?.due_before || '',
    due_after: filterParams?.due_after || '',
  };

  if (loading) {
    return (
      <div>
        {hasFilterBar && (
          <div className="mb-4 space-y-3">
            <div className="flex flex-wrap gap-3 items-center">
              <div className="flex-1 min-w-48"><SearchBar value={filterParams?.search || ''} onChange={handleSearch} /></div>
              <FilterPanel filters={currentFilters} onChange={handleFilterChange} />
              <SortControl sortBy={filterParams?.sort_by || 'created_at'} sortDir={filterParams?.sort_dir || 'desc'} onChange={handleSortChange} />
            </div>
          </div>
        )}
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-300">Loading tasks...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 mb-4">
        <p className="text-sm text-red-700 dark:text-red-300"><strong>Error:</strong> {error}</p>
      </div>
    );
  }

  return (
    <div>
      {hasFilterBar && (
        <div className="mb-4 space-y-3">
          <div className="flex flex-wrap gap-3 items-center">
            <div className="flex-1 min-w-48">
              <SearchBar value={filterParams?.search || ''} onChange={handleSearch} />
            </div>
            <FilterPanel filters={currentFilters} onChange={handleFilterChange} />
            <SortControl sortBy={filterParams?.sort_by || 'created_at'} sortDir={filterParams?.sort_dir || 'desc'} onChange={handleSortChange} />
          </div>
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No tasks</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{emptyMessage}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={() => onTaskToggle(task.id)}
              onDelete={() => onTaskDelete(task.id)}
              onUpdate={(updatedTask) => onTaskUpdate(task.id, updatedTask)}
            />
          ))}
          {totalCount !== undefined && totalCount > tasks.length && (
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 py-2">
              Showing {tasks.length} of {totalCount} tasks
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default TaskList;
