import React, { createContext, useContext, useState, useEffect } from 'react';
import offlineService from '../services/offlineService';

const OfflineContext = createContext();

export const useOffline = () => {
  const context = useContext(OfflineContext);
  if (!context) {
    throw new Error('useOffline must be used within an OfflineProvider');
  }
  return context;
};

export const OfflineProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncStatus, setSyncStatus] = useState({
    inProgress: false,
    queueSize: 0,
    lastSync: null
  });
  const [cacheSize, setCacheSize] = useState({ total: 0 });

  useEffect(() => {
    // Listen for network status changes
    const handleNetworkChange = (event) => {
      setIsOnline(event.detail.isOnline);
    };

    // Listen for sync completion
    const handleSyncComplete = (event) => {
      setSyncStatus(prev => ({
        ...prev,
        inProgress: false,
        lastSync: event.detail.timestamp
      }));
      localStorage.setItem('lastSyncTime', event.detail.timestamp);
      updateCacheSize();
    };

    // Listen for sync start
    const handleSyncStart = () => {
      setSyncStatus(prev => ({
        ...prev,
        inProgress: true
      }));
    };

    window.addEventListener('networkStatusChange', handleNetworkChange);
    window.addEventListener('syncComplete', handleSyncComplete);
    window.addEventListener('syncStart', handleSyncStart);

    // Initialize cache size
    updateCacheSize();

    // Update sync status periodically
    const statusInterval = setInterval(() => {
      const status = offlineService.getSyncStatus();
      setSyncStatus(prev => ({
        ...prev,
        queueSize: status.queueSize,
        lastSync: status.lastSync
      }));
    }, 5000);

    return () => {
      window.removeEventListener('networkStatusChange', handleNetworkChange);
      window.removeEventListener('syncComplete', handleSyncComplete);
      window.removeEventListener('syncStart', handleSyncStart);
      clearInterval(statusInterval);
    };
  }, []);

  const updateCacheSize = async () => {
    try {
      const size = await offlineService.getCacheSize();
      setCacheSize(size);
    } catch (error) {
      console.error('Failed to get cache size:', error);
    }
  };

  const manualSync = async () => {
    if (!isOnline) {
      throw new Error('Cannot sync while offline');
    }
    
    setSyncStatus(prev => ({ ...prev, inProgress: true }));
    
    try {
      await offlineService.performSync();
    } catch (error) {
      console.error('Manual sync failed:', error);
      throw error;
    } finally {
      setSyncStatus(prev => ({ ...prev, inProgress: false }));
    }
  };

  const clearOfflineData = async () => {
    try {
      await offlineService.clearCache();
      await updateCacheSize();
    } catch (error) {
      console.error('Failed to clear offline data:', error);
      throw error;
    }
  };

  // Offline-aware task operations
  const createTaskOffline = async (taskData) => {
    try {
      const task = await offlineService.saveTask(taskData);
      return { success: true, task };
    } catch (error) {
      console.error('Failed to create task offline:', error);
      return { success: false, error: error.message };
    }
  };

  const updateTaskOffline = async (taskId, updates) => {
    try {
      const task = await offlineService.updateTask(taskId, updates);
      return { success: true, task };
    } catch (error) {
      console.error('Failed to update task offline:', error);
      return { success: false, error: error.message };
    }
  };

  const deleteTaskOffline = async (taskId) => {
    try {
      await offlineService.deleteTask(taskId);
      return { success: true };
    } catch (error) {
      console.error('Failed to delete task offline:', error);
      return { success: false, error: error.message };
    }
  };

  const getTasksOffline = async (userId) => {
    try {
      const tasks = await offlineService.getTasks(userId);
      return { success: true, tasks };
    } catch (error) {
      console.error('Failed to get tasks offline:', error);
      return { success: false, error: error.message };
    }
  };

  const saveUserDataOffline = async (key, data) => {
    try {
      await offlineService.saveUserData(key, data);
      return { success: true };
    } catch (error) {
      console.error('Failed to save user data offline:', error);
      return { success: false, error: error.message };
    }
  };

  const getUserDataOffline = async (key) => {
    try {
      const data = await offlineService.getUserData(key);
      return { success: true, data };
    } catch (error) {
      console.error('Failed to get user data offline:', error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    // Status
    isOnline,
    syncStatus,
    cacheSize,
    
    // Actions
    manualSync,
    clearOfflineData,
    updateCacheSize,
    
    // Offline operations
    createTaskOffline,
    updateTaskOffline,
    deleteTaskOffline,
    getTasksOffline,
    saveUserDataOffline,
    getUserDataOffline,
    
    // Service reference
    offlineService
  };

  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
};