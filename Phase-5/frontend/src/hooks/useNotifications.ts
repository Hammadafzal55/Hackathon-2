'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../lib/api';
import type { NotificationRead } from '../types/notification';

interface NotificationsState {
  notifications: NotificationRead[];
  unreadCount: number;
  loading: boolean;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useNotifications = (): NotificationsState => {
  const [notifications, setNotifications] = useState<NotificationRead[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const inflightRef = useRef(false);

  const fetchNotifications = useCallback(async () => {
    if (inflightRef.current) return;
    inflightRef.current = true;
    try {
      const data = await apiClient.getNotifications(undefined, 20, 0);
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.warn('Failed to fetch notifications:', err);
    } finally {
      inflightRef.current = false;
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    intervalRef.current = setInterval(fetchNotifications, 60000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchNotifications]);

  const markRead = useCallback(async (id: string) => {
    try {
      await apiClient.markNotificationRead(id);
      setNotifications(prev => prev.map(n => (n.id === id ? { ...n, read: true } : n)));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification read:', err);
    }
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await apiClient.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all notifications read:', err);
    }
  }, []);

  return { notifications, unreadCount, loading, markRead, markAllRead, refresh: fetchNotifications };
};
