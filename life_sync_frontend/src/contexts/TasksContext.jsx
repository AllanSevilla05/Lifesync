import { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import ApiService from '../services/api';
import { useAuth } from './AuthContext';

const TasksContext = createContext({});

export const useTasks = () => {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error('useTasks must be used within a TasksProvider');
  }
  return context;
};

export const TasksProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();

  const fetchTasks = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await ApiService.getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const createTask = async (taskData) => {
    try {
      setError(null);
      const newTask = await ApiService.createTask(taskData);
      setTasks(prev => [...prev, newTask]);
      return { success: true, data: newTask };
    } catch (err) {
      console.error('Failed to create task:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      setError(null);
      const updatedTask = await ApiService.updateTask(taskId, updates);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ));
      return { success: true, data: updatedTask };
    } catch (err) {
      console.error('Failed to update task:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setError(null);
      await ApiService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      return { success: true };
    } catch (err) {
      console.error('Failed to delete task:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const createTasksFromVoice = async (voiceText, context = "") => {
    try {
      setError(null);
      const newTasks = await ApiService.createTasksFromVoice({
        voice_text: voiceText,
        context: context
      });
      setTasks(prev => [...prev, ...newTasks]);
      return { success: true, data: newTasks };
    } catch (err) {
      console.error('Failed to create tasks from voice:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  // Load tasks when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
    } else {
      setTasks([]);
    }
  }, [isAuthenticated, fetchTasks]);

  // Helper functions to categorize tasks
  const getPastDueTasks = useMemo(() => {
    const now = new Date();
    return tasks.filter(task => {
      if (!task.due_date || task.status === 'completed') return false;
      return new Date(task.due_date) < now;
    });
  }, [tasks]);

  const getUpcomingTasks = useMemo(() => {
    const now = new Date();
    return tasks.filter(task => {
      if (!task.due_date || task.status === 'completed') return false;
      return new Date(task.due_date) >= now;
    });
  }, [tasks]);

  const value = useMemo(() => ({
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    createTasksFromVoice,
    getPastDueTasks,
    getUpcomingTasks,
  }), [tasks, loading, error, fetchTasks, getPastDueTasks, getUpcomingTasks]);

  return (
    <TasksContext.Provider value={value}>
      {children}
    </TasksContext.Provider>
  );
};