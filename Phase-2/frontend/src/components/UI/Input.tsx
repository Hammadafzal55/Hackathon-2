import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  containerClassName?: string;
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  containerClassName = '',
  className = '',
  ...props
}) => {
  const inputClass = `w-full px-4 py-3 bg-white/20 dark:bg-gray-800/30 border ${
    error
      ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
      : 'border-white/30 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500'
  } rounded-lg focus:ring-2 focus:outline-none transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 ${className}`;

  return (
    <div className={`space-y-2 ${containerClassName}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <input
        className={inputClass}
        {...props}
      />
      {helperText && !error && (
        <p className="text-xs text-gray-500 dark:text-gray-400">{helperText}</p>
      )}
      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
};

export default Input;