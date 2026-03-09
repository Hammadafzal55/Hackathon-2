'use client';

import React from 'react';
import { RecurrenceRule } from '../../types/task';

interface RecurrenceFormProps {
  value: RecurrenceRule | null;
  onChange: (rule: RecurrenceRule | null) => void;
}

const PATTERNS: Array<{ value: RecurrenceRule['pattern']; label: string }> = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
];

export const RecurrenceForm: React.FC<RecurrenceFormProps> = ({ value, onChange }) => {
  const isEnabled = value !== null;

  const handleToggle = () => {
    if (isEnabled) {
      onChange(null);
    } else {
      onChange({ pattern: 'daily', interval: 1, end_condition: 'never' });
    }
  };

  const update = (updates: Partial<RecurrenceRule>) => {
    if (value) onChange({ ...value, ...updates });
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={handleToggle}
          className={`relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
            isEnabled ? 'bg-blue-500' : 'bg-gray-400/50'
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
              isEnabled ? 'translate-x-5' : 'translate-x-0'
            }`}
          />
        </button>
        <span className="text-sm font-medium text-gray-200">Repeat this task</span>
      </div>

      {isEnabled && value && (
        <div className="ml-4 space-y-3 p-3 bg-white/5 rounded-lg border border-white/10">
          <div className="flex items-center gap-3">
            <label className="text-xs text-gray-400 w-16">Pattern</label>
            <select
              value={value.pattern}
              onChange={e => update({ pattern: e.target.value as RecurrenceRule['pattern'] })}
              className="flex-1 px-2 py-1 bg-white/10 border border-white/20 rounded text-sm text-white"
            >
              {PATTERNS.map(p => (
                <option key={p.value} value={p.value} className="bg-gray-800">{p.label}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3">
            <label className="text-xs text-gray-400 w-16">Every</label>
            <input
              type="number"
              min={1}
              max={99}
              value={value.interval}
              onChange={e => update({ interval: Math.max(1, parseInt(e.target.value) || 1) })}
              className="w-16 px-2 py-1 bg-white/10 border border-white/20 rounded text-sm text-white text-center"
            />
            <span className="text-xs text-gray-400">{value.pattern.replace('ly', '(s)')}</span>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-gray-400">Ends</label>
            <div className="space-y-2">
              {[
                { value: 'never', label: 'Never' },
                { value: 'after_n', label: 'After N occurrences' },
                { value: 'by_date', label: 'By date' },
              ].map(opt => (
                <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="end_condition"
                    value={opt.value}
                    checked={value.end_condition === opt.value}
                    onChange={() => update({ end_condition: opt.value as RecurrenceRule['end_condition'] })}
                    className="accent-blue-500"
                  />
                  <span className="text-xs text-gray-300">{opt.label}</span>
                  {opt.value === 'after_n' && value.end_condition === 'after_n' && (
                    <input
                      type="number"
                      min={1}
                      value={value.end_after_n || 1}
                      onChange={e => update({ end_after_n: parseInt(e.target.value) || 1 })}
                      className="w-16 px-2 py-0.5 bg-white/10 border border-white/20 rounded text-sm text-white text-center"
                    />
                  )}
                  {opt.value === 'by_date' && value.end_condition === 'by_date' && (
                    <input
                      type="date"
                      value={value.end_by_date || ''}
                      onChange={e => update({ end_by_date: e.target.value })}
                      className="px-2 py-0.5 bg-white/10 border border-white/20 rounded text-sm text-white"
                    />
                  )}
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
