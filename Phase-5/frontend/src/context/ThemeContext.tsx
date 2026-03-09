'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Define theme types
type ThemeMode = 'light' | 'dark';
type ThemeColors = {
  primary: string;
  secondary: string;
  background: string;
  text: string;
  accent: string;
};

// Define the theme structure
interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
  borderRadius: string;
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}

// Define context type
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
}

// Create the context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Define default themes
const lightTheme: Theme = {
  mode: 'light',
  colors: {
    primary: '#3b82f6', // blue-500
    secondary: '#60a5fa', // blue-400
    background: '#ffffff',
    text: '#1f2937', // gray-800
    accent: '#f3f4f6', // gray-100
  },
  borderRadius: '0.5rem',
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
};

const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    primary: '#60a5fa', // blue-400
    secondary: '#93c5fd', // blue-300
    background: '#111827', // gray-900
    text: '#f9fafb', // gray-50
    accent: '#1f2937', // gray-800
  },
  borderRadius: '0.5rem',
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
};

// Theme Provider Component
export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setThemeState] = useState<Theme>(lightTheme);

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as ThemeMode | null;
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
      setThemeState(savedTheme === 'dark' ? darkTheme : lightTheme);
    } else if (systemPrefersDark) {
      setThemeState(darkTheme);
    }
  }, []);

  // Update document class, CSS variables and localStorage when theme changes
  useEffect(() => {
    // Apply dark class to html element for Tailwind dark mode
    if (theme.mode === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }

    // Update CSS variables based on current theme
    if (theme.mode === 'light') {
      document.documentElement.style.setProperty('--background', theme.colors.background);
      document.documentElement.style.setProperty('--foreground', theme.colors.text);
      document.documentElement.style.setProperty('--primary', theme.colors.primary);
      document.documentElement.style.setProperty('--primary-foreground', '#f9fafb');
      document.documentElement.style.setProperty('--secondary', theme.colors.accent);
      document.documentElement.style.setProperty('--secondary-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--accent', theme.colors.accent);
      document.documentElement.style.setProperty('--accent-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--card', theme.colors.background);
      document.documentElement.style.setProperty('--card-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--border', '#e5e7eb');
      document.documentElement.style.setProperty('--input', '#e5e7eb');
      document.documentElement.style.setProperty('--ring', theme.colors.primary);

      // Light mode glassmorphism variables
      document.documentElement.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.8)');
      document.documentElement.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.8)');
      document.documentElement.style.setProperty('--glass-shadow', '0 8px 32px 0 rgba(31, 38, 135, 0.4)');
    } else {
      document.documentElement.style.setProperty('--background', theme.colors.background);
      document.documentElement.style.setProperty('--foreground', theme.colors.text);
      document.documentElement.style.setProperty('--primary', theme.colors.primary);
      document.documentElement.style.setProperty('--primary-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--secondary', theme.colors.accent);
      document.documentElement.style.setProperty('--secondary-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--accent', theme.colors.accent);
      document.documentElement.style.setProperty('--accent-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--card', theme.colors.background);
      document.documentElement.style.setProperty('--card-foreground', theme.colors.text);
      document.documentElement.style.setProperty('--border', '#374151');
      document.documentElement.style.setProperty('--input', '#374151');
      document.documentElement.style.setProperty('--ring', theme.colors.primary);

      // Dark mode glassmorphism variables
      document.documentElement.style.setProperty('--glass-bg', 'rgba(30, 41, 59, 0.5)');
      document.documentElement.style.setProperty('--glass-border', 'rgba(255, 255, 255, 0.35)');
      document.documentElement.style.setProperty('--glass-shadow', '0 8px 32px 0 rgba(30, 41, 59, 0.5)');
    }

    localStorage.setItem('theme', theme.mode);
  }, [theme]);

  const toggleTheme = () => {
    setThemeState(prev => prev.mode === 'light' ? darkTheme : lightTheme);
  };

  const setTheme = (mode: ThemeMode) => {
    setThemeState(mode === 'light' ? lightTheme : darkTheme);
  };

  const value = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};