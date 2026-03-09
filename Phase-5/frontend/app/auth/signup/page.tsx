'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/src/providers/AuthProvider';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { signUp, loading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      await signUp(email, password, firstName, lastName, username);

      // Reset the form fields
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setFirstName('');
      setLastName('');
      setUsername('');

      // Redirect to login page after successful signup
      router.push('/auth/login');
    } catch (err) {
      setError('Registration failed. Please check your information.');
      console.error('Signup error:', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#121212] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full p-[24px] bg-[#1d1d1d] rounded-[8px] border border-white/20 shadow-lg space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-[rgba(255,255,255,0.87)]">
            Create an account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-500/20 p-4">
              <div className="text-sm text-red-300">{error}</div>
            </div>
          )}
          <input type="hidden" name="remember" defaultValue="true" />
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="first-name" className="sr-only">
                First Name
              </label>
              <input
                id="first-name"
                name="first-name"
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm mb-4"
                placeholder="First Name"
              />
            </div>
            <div>
              <label htmlFor="last-name" className="sr-only">
                Last Name
              </label>
              <input
                id="last-name"
                name="last-name"
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm mb-4"
                placeholder="Last Name"
              />
            </div>
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm mb-4"
                placeholder="Username"
              />
            </div>
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm mb-4"
                placeholder="Email address"
              />
            </div>
            <div className="relative mb-4">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm pr-10"
                placeholder="Password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-200 z-10"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                  </svg>
                )}
              </button>
            </div>
            <div className="relative">
              <label htmlFor="confirm-password" className="sr-only">
                Confirm Password
              </label>
              <input
                id="confirm-password"
                name="confirm-password"
                type={showPassword ? "text" : "password"} // Using showPassword for both password fields
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-[#979797] placeholder-gray-500 text-[rgba(255,255,255,0.87)] bg-[#1d1d1d] focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm pr-10"
                placeholder="Confirm Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-[#8875ff] text-sm font-medium rounded-md text-[rgba(255,255,255,0.87)] bg-[rgba(134,135,231,0.5)] hover:bg-[rgba(134,135,231,0.7)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#8875ff] disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>

          <div className="text-center mt-4">
            <p className="text-sm text-[#979797]">
              Already have an account?{' '}
              <a href="/auth/login" className="font-medium text-[#8875ff] hover:text-[#7a6cfd]">
                Sign in
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}