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
    try {
      const result = await authClient.signIn.email({
        email,
        password,
        callbackURL: "/tasks", // Redirect to tasks after sign in
      });

      if (result?.data?.user) {
        // Simply set the user from Better Auth session - no backend verification needed
        setUser(result.data.user as unknown as User);
      }

      return result;
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
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
    try {
      // Combine firstName and lastName into the name field
      const fullName = `${firstName} ${lastName}`.trim();
      const result = await authClient.signUp.email({
        email,
        password,
        name: fullName, // Use the standard 'name' field
        callbackURL: "/auth/login", // Redirect to login after sign up
      });
      if (result?.data?.user) {
        setUser(result.data.user as unknown as User);
      }
      return result;
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
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