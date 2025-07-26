import { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import ApiService from '../services/api';
import { useAuth } from './AuthContext';
import { useOffline } from './OfflineContext';

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
  const { isAuthenticated, user } = useAuth();
  const { 
    isOnline, 
    createTaskOffline, 
    updateTaskOffline, 
    deleteTaskOffline, 
    getTasksOffline 
  } = useOffline();

  const fetchTasks = useCallback(async () => {
    if (!isAuthenticated || !user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      if (isOnline) {
        // Try to fetch from server first
        try {
          const fetchedTasks = await ApiService.getTasks();
          setTasks(fetchedTasks);
        } catch (err) {
          // If server fails but we're online, fall back to offline data
          console.warn('Server fetch failed, using offline data:', err);
          const offlineResult = await getTasksOffline(user.id);
          if (offlineResult.success) {
            setTasks(offlineResult.tasks);
          }
        }
      } else {
        // Load from offline storage
        const offlineResult = await getTasksOffline(user.id);
        if (offlineResult.success) {
          setTasks(offlineResult.tasks);
        } else {
          setError('Unable to load tasks offline');
        }
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, isOnline, getTasksOffline]);

  const createTask = async (taskData) => {
    try {
      setError(null);
      
      if (isOnline) {
        try {
          const newTask = await ApiService.createTask(taskData);
          setTasks(prev => [...prev, newTask]);
          return { success: true, data: newTask };
        } catch (err) {
          // If online request fails, save offline
          console.warn('Online create failed, saving offline:', err);
          const offlineResult = await createTaskOffline({
            ...taskData,
            id: `temp_${Date.now()}`, // Temporary ID for offline tasks
            user_id: user.id,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
          
          if (offlineResult.success) {
            setTasks(prev => [...prev, offlineResult.task]);
            return { success: true, data: offlineResult.task, offline: true };
          }
          throw err;
        }
      } else {
        // Create task offline
        const offlineResult = await createTaskOffline({
          ...taskData,
          id: `temp_${Date.now()}`,
          user_id: user.id,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
        
        if (offlineResult.success) {
          setTasks(prev => [...prev, offlineResult.task]);
          return { success: true, data: offlineResult.task, offline: true };
        }
        
        throw new Error(offlineResult.error);
      }
    } catch (err) {
      console.error('Failed to create task:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      setError(null);
      
      if (isOnline) {
        try {
          const updatedTask = await ApiService.updateTask(taskId, updates);
          setTasks(prev => prev.map(task => 
            task.id === taskId ? updatedTask : task
          ));
          return { success: true, data: updatedTask };
        } catch (err) {
          // If online request fails, update offline
          console.warn('Online update failed, updating offline:', err);
          const offlineResult = await updateTaskOffline(taskId, {
            ...updates,
            updated_at: new Date().toISOString()
          });
          
          if (offlineResult.success) {
            setTasks(prev => prev.map(task => 
              task.id === taskId ? offlineResult.task : task
            ));
            return { success: true, data: offlineResult.task, offline: true };
          }
          throw err;
        }
      } else {
        // Update task offline
        const offlineResult = await updateTaskOffline(taskId, {
          ...updates,
          updated_at: new Date().toISOString()
        });
        
        if (offlineResult.success) {
          setTasks(prev => prev.map(task => 
            task.id === taskId ? offlineResult.task : task
          ));
          return { success: true, data: offlineResult.task, offline: true };
        }
        
        throw new Error(offlineResult.error);
      }
    } catch (err) {
      console.error('Failed to update task:', err);
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setError(null);
      
      if (isOnline) {
        try {
          await ApiService.deleteTask(taskId);
          setTasks(prev => prev.filter(task => task.id !== taskId));
          return { success: true };
        } catch (err) {
          // If online request fails, delete offline
          console.warn('Online delete failed, deleting offline:', err);
          const offlineResult = await deleteTaskOffline(taskId);
          
          if (offlineResult.success) {
            setTasks(prev => prev.filter(task => task.id !== taskId));
            return { success: true, offline: true };
          }
          throw err;
        }
      } else {
        // Delete task offline
        const offlineResult = await deleteTaskOffline(taskId);
        
        if (offlineResult.success) {
          setTasks(prev => prev.filter(task => task.id !== taskId));
          return { success: true, offline: true };
        }
        
        throw new Error(offlineResult.error);
      }
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