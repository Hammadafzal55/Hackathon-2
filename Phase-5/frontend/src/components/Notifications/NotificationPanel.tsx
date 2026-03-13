'use client';

import React from 'react';
import type { NotificationRead } from '../../types/notification';

interface NotificationPanelProps {
  notifications: NotificationRead[];
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
  onClose: () => void;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export const NotificationPanel: React.FC<NotificationPanelProps> = ({
  notifications,
  onMarkRead,
  onMarkAllRead,
  onClose,
}) => {
  const hasUnread = notifications.some(n => !n.read);

  return (
    <div className="absolute right-0 top-full mt-2 w-80 bg-gray-800/95 backdrop-blur border border-white/20 rounded-xl shadow-2xl z-50 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <span className="text-sm font-semibold text-white">Notifications</span>
        <div className="flex items-center gap-3">
          {hasUnread && (
            <button
              onClick={onMarkAllRead}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              Mark all read
            </button>
          )}
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="px-4 py-8 text-center text-gray-400 text-sm">
            No notifications
          </div>
        ) : (
          notifications.map(n => (
            <div
              key={n.id}
              onClick={() => { if (!n.read) onMarkRead(n.id); }}
              className={`px-4 py-3 border-b border-white/5 cursor-pointer hover:bg-white/5 transition-colors ${
                !n.read ? 'bg-blue-500/5' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                {!n.read && (
                  <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500" />
                )}
                <div className={!n.read ? '' : 'pl-5'}>
                  <p className="text-sm text-gray-200 leading-snug">{n.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{timeAgo(n.created_at)}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
