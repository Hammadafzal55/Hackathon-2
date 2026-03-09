'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useNotifications } from '../../hooks/useNotifications';
import { NotificationPanel } from './NotificationPanel';

export const NotificationBell: React.FC = () => {
  const [panelOpen, setPanelOpen] = useState(false);
  const { notifications, unreadCount, markRead, markAllRead } = useNotifications();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setPanelOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setPanelOpen(!panelOpen)}
        className="relative p-2 rounded-full glass border border-white/20 backdrop-blur-sm hover:scale-105 transition-transform"
        aria-label="Notifications"
      >
        <svg className="h-5 w-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-4 w-4 flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {panelOpen && (
        <NotificationPanel
          notifications={notifications}
          onMarkRead={markRead}
          onMarkAllRead={markAllRead}
          onClose={() => setPanelOpen(false)}
        />
      )}
    </div>
  );
};
