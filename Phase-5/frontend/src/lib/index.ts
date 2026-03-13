// Export API client and related types
export {
  apiClient,
  fetchTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskCompletion,
  type ApiError
} from './api';

export type {
  Task,
  TaskCreate,
  TaskUpdate
} from '../types/task';

export {
  isTask,
  isTaskCreate,
  isTaskUpdate,
  isTaskArray
} from './api';