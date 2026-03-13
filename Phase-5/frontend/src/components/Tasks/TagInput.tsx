'use client';

import React, { useState, useRef } from 'react';
import { useTags } from '../../hooks/useTags';

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
}

export const TagInput: React.FC<TagInputProps> = ({ value = [], onChange }) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { tags: allTags } = useTags();
  const inputRef = useRef<HTMLInputElement>(null);

  const suggestions = allTags.filter(
    t => t.toLowerCase().includes(inputValue.toLowerCase()) && !value.includes(t)
  );

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInputValue('');
    setShowSuggestions(false);
  };

  const removeTag = (tag: string) => {
    onChange(value.filter(t => t !== tag));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      if (inputValue.trim()) addTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  return (
    <div className="relative">
      <div
        className="flex flex-wrap gap-1.5 p-2 min-h-[40px] bg-white/10 border border-white/20 rounded-lg cursor-text"
        onClick={() => inputRef.current?.focus()}
      >
        {value.map(tag => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-500/20 border border-blue-400/30 rounded-full text-xs text-blue-300"
          >
            {tag}
            <button
              type="button"
              onClick={e => { e.stopPropagation(); removeTag(tag); }}
              className="hover:text-red-400 transition-colors leading-none"
            >
              &times;
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={e => { setInputValue(e.target.value); setShowSuggestions(true); }}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
          placeholder={value.length === 0 ? 'Add tags...' : ''}
          className="flex-1 min-w-[80px] bg-transparent text-sm text-white outline-none placeholder-gray-400"
        />
      </div>
      {showSuggestions && suggestions.length > 0 && inputValue && (
        <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-white/20 rounded-lg shadow-xl max-h-36 overflow-y-auto">
          {suggestions.map(tag => (
            <button
              key={tag}
              type="button"
              onMouseDown={() => addTag(tag)}
              className="w-full px-3 py-1.5 text-left text-sm text-gray-200 hover:bg-white/10 transition-colors"
            >
              {tag}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
