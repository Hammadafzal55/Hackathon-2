export interface NotificationRead {
  id: string;
  user_id: string;
  task_id: string | null;
  message: string;
  read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: NotificationRead[];
  total_count: number;
  unread_count: number;
}
