'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface GlassButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}

const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  onClick,
  href,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
}) => {
  const baseClasses = `
    relative overflow-hidden
    border border-white/20
    backdrop-blur-md
    transition-all duration-300
    transform hover:scale-105 active:scale-95
    focus:outline-none focus:ring-2 focus:ring-white/50
    disabled:opacity-50 disabled:cursor-not-allowed
    group
  `;

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm rounded-lg',
    md: 'px-6 py-3 text-base rounded-xl',
    lg: 'px-8 py-4 text-lg rounded-2xl',
  };

  const variantClasses = {
    primary: `
      bg-blue-500/40
      text-white
      hover:bg-blue-500/50
      shadow-lg shadow-blue-500/30
      hover:shadow-xl hover:shadow-blue-500/40
    `,
    secondary: `
      bg-indigo-500/30
      text-white
      hover:bg-indigo-500/40
      shadow-lg shadow-indigo-500/20
      hover:shadow-xl hover:shadow-indigo-500/30
    `,
  };

  const buttonClasses = `${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`;

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement | HTMLButtonElement>) => {
    if (disabled) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick();
    }
  };

  // Render anchor tag if href is provided
  if (href) {
    return (
      <motion.a
        href={href}
        className={buttonClasses}
        onClick={handleClick}
        whileHover={{ scale: disabled ? 1 : 1.02 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
      >
        <span className="relative z-10">{children}</span>
        {/* Shine effect */}
        <motion.span
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"
          initial={false}
        />
      </motion.a>
    );
  }

  return (
    <motion.button
      className={buttonClasses}
      onClick={handleClick}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      disabled={disabled}
    >
      <span className="relative z-10">{children}</span>
      {/* Shine effect */}
      <motion.span
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out"
        initial={false}
      />
    </motion.button>
  );
};

export default GlassButton;
