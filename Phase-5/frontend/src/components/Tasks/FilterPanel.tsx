'use client';

import React, { useState } from 'react';
import { useTags } from '../../hooks/useTags';

export interface FilterState {
  status: string[];
  priority: string[];
  tags: string[];
  due_before: string;
  due_after: string;
}

interface FilterPanelProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

const STATUSES = ['pending', 'in_progress', 'completed', 'cancelled'];
const PRIORITIES = [
  { value: '1', label: 'Low' },
  { value: '2', label: 'Medium' },
  { value: '3', label: 'High' },
  { value: '4', label: 'Very High' },
  { value: '5', label: 'Critical' },
];

export const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onChange }) => {
  const [open, setOpen] = useState(false);
  const { tags: allTags } = useTags();

  const activeCount =
    filters.status.length + filters.priority.length + filters.tags.length +
    (filters.due_before ? 1 : 0) + (filters.due_after ? 1 : 0);

  const toggle = <K extends keyof Pick<FilterState, 'status' | 'priority' | 'tags'>>(key: K, val: string) => {
    const arr = filters[key] as string[];
    onChange({ ...filters, [key]: arr.includes(val) ? arr.filter(x => x !== val) : [...arr, val] });
  };

  const clearAll = () => onChange({ status: [], priority: [], tags: [], due_before: '', due_after: '' });

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm border transition-colors ${
          activeCount > 0
            ? 'bg-blue-500/20 border-blue-400/40 text-blue-300'
            : 'bg-white/10 border-white/20 text-gray-300 hover:bg-white/15'
        }`}
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filters
        {activeCount > 0 && (
          <span className="bg-blue-500 text-white text-xs px-1.5 py-0.5 rounded-full">{activeCount}</span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-72 bg-gray-800/95 backdrop-blur border border-white/20 rounded-xl shadow-2xl z-20 p-4 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-white">Filters</span>
            {activeCount > 0 && (
              <button onClick={clearAll} className="text-xs text-gray-400 hover:text-red-400 transition-colors">
                Clear all
              </button>
            )}
          </div>

          {/* Status */}
          <div>
            <p className="text-xs text-gray-400 mb-2">Status</p>
            <div className="flex flex-wrap gap-1.5">
              {STATUSES.map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggle('status', s)}
                  className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                    filters.status.includes(s)
                      ? 'bg-blue-500/30 border-blue-400/50 text-blue-300'
                      : 'bg-white/5 border-white/20 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {s.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Priority */}
          <div>
            <p className="text-xs text-gray-400 mb-2">Priority</p>
            <div className="flex flex-wrap gap-1.5">
              {PRIORITIES.map(p => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => toggle('priority', p.value)}
                  className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                    filters.priority.includes(p.value)
                      ? 'bg-amber-500/30 border-amber-400/50 text-amber-300'
                      : 'bg-white/5 border-white/20 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tags */}
          {allTags.length > 0 && (
            <div>
              <p className="text-xs text-gray-400 mb-2">Tags</p>
              <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                {allTags.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => toggle('tags', tag)}
                    className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                      filters.tags.includes(tag)
                        ? 'bg-purple-500/30 border-purple-400/50 text-purple-300'
                        : 'bg-white/5 border-white/20 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Due date range */}
          <div className="space-y-2">
            <p className="text-xs text-gray-400">Due Date Range</p>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="text-xs text-gray-500 mb-1">After</p>
                <input
                  type="date"
                  value={filters.due_after}
                  onChange={e => onChange({ ...filters, due_after: e.target.value })}
                  className="w-full px-2 py-1 bg-white/10 border border-white/20 rounded text-xs text-white"
                />
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Before</p>
                <input
                  type="date"
                  value={filters.due_before}
                  onChange={e => onChange({ ...filters, due_before: e.target.value })}
                  className="w-full px-2 py-1 bg-white/10 border border-white/20 rounded text-xs text-white"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
