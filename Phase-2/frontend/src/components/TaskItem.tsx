'use client';

import React from 'react';
import { Task } from '../types/task';
import TaskCardEnhanced from './TaskCard/TaskCardEnhanced';

interface TaskItemProps {
  task: Task;
  onToggle: () => void;
  onDelete: () => void;
  onUpdate: (updatedTask: Partial<Task>) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete, onUpdate }) => {
  return (
    <TaskCardEnhanced
      task={task}
      onToggle={onToggle}
      onDelete={onDelete}
      onUpdate={onUpdate}
    />
  );
};

export default TaskItem;