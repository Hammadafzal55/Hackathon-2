'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/src/providers/AuthProvider';
import GlassButton from '../src/components/LandingPage/GlassButton';
import { motion } from 'framer-motion';

export default function Home() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      router.push('/tasks');
    } else {
      router.push('/auth/login');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <section className="relative py-20 px-4 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 dark:from-blue-900/20 dark:to-purple-900/20 -z-10"></div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-black dark:from-gray-100 dark:to-white">
            FlowTodo
          </h1>

          <motion.p
            className="text-2xl md:text-3xl font-light text-gray-700 dark:text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            Streamline your tasks with our beautifully designed todo application
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row justify-center gap-4 mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <GlassButton
              variant="primary"
              size="lg"
              onClick={handleGetStarted}
            >
              {user ? 'Go to Tasks' : 'Get Started'}
            </GlassButton>
            <GlassButton
              variant="secondary"
              size="lg"
              href="https://github.com/Hammadafzal55/Hackathon-2/tree/main/Phase-2"
            >
              Learn More
            </GlassButton>
          </motion.div>
        </motion.div>
      </section>

      {/* Feature Highlights */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Intuitive Interface",
                description: "Beautifully crafted UI with smooth interactions and delightful animations.",
                icon: "✨"
              },
              {
                title: "Smart Organization",
                description: "Effortlessly categorize and prioritize your tasks with smart features.",
                icon: "🎯"
              },
              {
                title: "Cross-Device Sync",
                description: "Access your tasks anywhere, anytime with seamless synchronization.",
                icon: "🔄"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="glass p-6 rounded-2xl border border-white/20 backdrop-blur-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.5 }}
                whileHover={{ y: -5 }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <footer className="container mx-auto px-4 py-8 text-center text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="mb-4">
          <div className="h-px w-16 bg-gray-300 dark:bg-gray-600 mx-auto mb-4"></div>
          <p>FlowTodo © {new Date().getFullYear()} - All rights reserved.</p>
        </div>
        <p className="text-sm">Designed with ❤️ for productive workflows</p>
      </footer>
    </div>
  );
}