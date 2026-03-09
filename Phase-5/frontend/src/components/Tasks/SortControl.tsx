'use client';

import React from 'react';

interface SortControlProps {
  sortBy: string;
  sortDir: 'asc' | 'desc';
  onChange: (sortBy: string, sortDir: 'asc' | 'desc') => void;
}

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Created' },
  { value: 'due_date', label: 'Due Date' },
  { value: 'priority', label: 'Priority' },
  { value: 'title', label: 'Title' },
  { value: 'updated_at', label: 'Updated' },
];

export const SortControl: React.FC<SortControlProps> = ({ sortBy, sortDir, onChange }) => {
  return (
    <div className="flex items-center gap-1">
      <select
        value={sortBy}
        onChange={e => onChange(e.target.value, sortDir)}
        className="px-2 py-2 bg-white/10 border border-white/20 rounded-l-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
      >
        {SORT_OPTIONS.map(o => (
          <option key={o.value} value={o.value} className="bg-gray-800">{o.label}</option>
        ))}
      </select>
      <button
        type="button"
        onClick={() => onChange(sortBy, sortDir === 'asc' ? 'desc' : 'asc')}
        className="px-3 py-2 bg-white/10 border border-white/20 border-l-0 rounded-r-lg text-sm text-gray-300 hover:bg-white/15 transition-colors"
        title={sortDir === 'asc' ? 'Ascending' : 'Descending'}
      >
        {sortDir === 'asc' ? '↑' : '↓'}
      </button>
    </div>
  );
};
