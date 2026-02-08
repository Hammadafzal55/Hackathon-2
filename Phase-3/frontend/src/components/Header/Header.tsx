'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '@/src/providers/AuthProvider';
import GlassButton from '../LandingPage/GlassButton';

const Header = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, loading, signOut } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/20 backdrop-blur-md bg-white/10 dark:bg-gray-900/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <div className="flex-shrink-0 flex items-center">
            <Link href="/" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              FlowTodo
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:block">
            <div className="ml-10 flex items-center space-x-4">
              {!user ? (
                <>
                  <GlassButton variant="secondary" size="sm" href="/auth/signup">
                    Sign Up
                  </GlassButton>
                  <GlassButton variant="primary" size="sm" href="/auth/login">
                    Sign In
                  </GlassButton>
                </>
              ) : (
                <>
                  <GlassButton variant="secondary" size="sm" href="/tasks">
                    Tasks
                  </GlassButton>
                  <GlassButton variant="primary" size="sm" onClick={handleSignOut}>
                    Sign Out
                  </GlassButton>
                </>
              )}

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="ml-4 p-2 rounded-full glass border border-white/20 backdrop-blur-sm hover:scale-105 transition-transform"
                aria-label={`Switch to ${theme.mode === 'light' ? 'dark' : 'light'} mode`}
              >
                {theme.mode === 'light' ? '🌙' : '☀️'}
              </button>
            </div>
          </nav>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={toggleTheme}
              className="mr-2 p-2 rounded-full glass border border-white/20 backdrop-blur-sm hover:scale-105 transition-transform"
              aria-label={`Switch to ${theme.mode === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme.mode === 'light' ? '🌙' : '☀️'}
            </button>

            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md glass border border-white/20 backdrop-blur-sm text-gray-700 dark:text-gray-300 hover:scale-105 transition-transform"
              aria-expanded={isMenuOpen}
            >
              <svg
                className="h-6 w-6"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden glass rounded-b-xl border-t border-white/20 backdrop-blur-sm">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {!user ? (
              <>
                <div className="px-2 py-2">
                  <GlassButton variant="secondary" size="sm" href="/auth/signup" className="w-full">
                    Sign Up
                  </GlassButton>
                </div>
                <div className="px-2 py-2">
                  <GlassButton variant="primary" size="sm" href="/auth/login" className="w-full">
                    Sign In
                  </GlassButton>
                </div>
              </>
            ) : (
              <>
                <div className="px-2 py-2">
                  <GlassButton variant="secondary" size="sm" href="/tasks" className="w-full">
                    Tasks
                  </GlassButton>
                </div>
                <div className="px-2 py-2">
                  <GlassButton variant="primary" size="sm" onClick={handleSignOut} className="w-full">
                    Sign Out
                  </GlassButton>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;