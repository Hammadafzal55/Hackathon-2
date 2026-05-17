'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authClient } from '@/src/lib/auth';
import { User } from '../types/user';

interface AuthContextType {
  user: User | null;
  canonicalUserId: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<any>;
  signOut: () => Promise<void>;
  signUp: (email: string, password: string, firstName: string, lastName: string, username: string) => Promise<any>;
  getSession: () => Promise<{ user: User } | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [canonicalUserId, setCanonicalUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check session on initial load
  useEffect(() => {
    const checkSession = async () => {
      try {
        const sessionData = await authClient.getSession();

        // Better Auth's getSession() returns Data<{ user, session } | null> | Error
        // Properly handle the response structure
        let userData = null;

        if (sessionData && 'data' in sessionData && sessionData.data) {
            // It's a Data object, so the actual data is in sessionData.data
            if (sessionData.data.user) {
                userData = sessionData.data.user;
            }
        } else if (sessionData && 'user' in sessionData) {
            // It's not a Data object, but has a user property directly
            userData = (sessionData as any).user;
        }

        if (userData) {
          const userId = userData.id; // Extract the stable user ID from session

          // Set the canonical user ID if not already set
          if (userId && !canonicalUserId) {
            setCanonicalUserId(userId);
          }

          // Only update user state if different from current user to prevent unnecessary re-renders
          setUser(prevUser => {
            if (!prevUser || JSON.stringify(prevUser) !== JSON.stringify(userData)) {
              return userData as unknown as User;
            }
            return prevUser; // Keep existing user to prevent flickering
          });
        }
        // If no user data found, do not change the existing state to prevent null flips
      } catch (error) {
        console.error('Error checking session:', error);
        // DON'T clear user state on error - this prevents losing auth state due to network issues
        // The user might still be authenticated, just had a temporary network issue
        console.warn('Keeping existing user state despite session check error');
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, []);

  const handleSignIn = async (email: string, password: string) => {
    const result = await authClient.signIn.email({
      email,
      password,
      callbackURL: "/tasks",
    });

    if (result?.error) {
      const status = result.error.status;
      const code = result.error.code;
      if (status === 401 || code === 'INVALID_EMAIL_OR_PASSWORD') {
        throw new Error('Invalid email or password.');
      } else if (status === 403) {
        throw new Error('Access denied. Please try again or clear your cookies.');
      } else if (status === 429) {
        throw new Error('Too many attempts. Please wait a moment and try again.');
      } else if (!navigator.onLine) {
        throw new Error('Network error. Please check your connection.');
      } else {
        throw new Error(result.error.message || 'Sign in failed. Please try again.');
      }
    }

    if (result?.data?.user) {
      setUser(result.data.user as unknown as User);
    }

    return result;
  };

  const handleSignOut = async () => {
    try {
      await authClient.signOut();
      // Clear the cached token in the API client to ensure fresh token on next login
      // Import the apiClient directly to clear the cached token
      const apiModule = await import('@/src/lib/api');
      if (apiModule.apiClient) {
        apiModule.apiClient.clearCachedToken();
      }
      setUser(null);
      setCanonicalUserId(null);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const handleSignUp = async (email: string, password: string, firstName: string, lastName: string, username: string) => {
    const fullName = `${firstName} ${lastName}`.trim();
    const result = await authClient.signUp.email({
      email,
      password,
      name: fullName,
      callbackURL: "/auth/login",
    });

    if (result?.error) {
      const status = result.error.status;
      const code = result.error.code;
      if (status === 422 || code === 'USER_ALREADY_EXISTS') {
        throw new Error('An account with this email already exists.');
      } else if (status === 400) {
        throw new Error('Invalid details. Please check your email and password (min 8 characters).');
      } else if (!navigator.onLine) {
        throw new Error('Network error. Please check your connection.');
      } else {
        throw new Error(result.error.message || 'Registration failed. Please try again.');
      }
    }

    if (result?.data?.user) {
      setUser(result.data.user as unknown as User);
    }
    return result;
  };

  const getCurrentSession = async (): Promise<{ user: User } | null> => {
    try {
      const sessionData = await authClient.getSession();

              // Better Auth's getSession() returns Data<{ user, session } | null> | Error
              // Properly handle the response structure
              let userData = null;
      
              if (sessionData && 'data' in sessionData && sessionData.data) {
                  // It's a Data object, so the actual data is in sessionData.data
                  if (sessionData.data.user) {
                      userData = sessionData.data.user;
                  }
              } else if (sessionData && 'user' in sessionData) {
                  // It's not a Data object, but has a user property directly
                  userData = (sessionData as any).user;
              }
      if (userData) {
        const userId = userData.id; // Extract the stable user ID from session

        // Set the canonical user ID if not already set
        if (userId && !canonicalUserId) {
          setCanonicalUserId(userId);
        }

        // Only update user state if different from current user to prevent unnecessary re-renders
        setUser(prevUser => {
          if (!prevUser || JSON.stringify(prevUser) !== JSON.stringify(userData)) {
            return userData as unknown as User;
          }
          return prevUser; // Keep existing user to prevent flickering
        });
        return { user: userData as unknown as User };
      } else {
        // Do not set user to null if they were previously authenticated
        // Only return null without changing the state
        return null;
      }
    } catch (error) {
      console.error('Get session error:', error);
      return null;
    }
  };

  const value = {
    user,
    canonicalUserId,
    loading,
    signIn: handleSignIn,
    signOut: handleSignOut,
    signUp: handleSignUp,
    getSession: getCurrentSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};