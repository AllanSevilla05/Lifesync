class OfflineService {
  constructor() {
    this.dbName = 'LifeSyncOfflineDB';
    this.dbVersion = 1;
    this.db = null;
    this.isOnline = navigator.onLine;
    this.syncQueue = [];
    this.syncInProgress = false;
    
    this.initializeDB();
    this.setupNetworkListeners();
    this.registerServiceWorker();
  }

  async initializeDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Tasks store
        if (!db.objectStoreNames.contains('tasks')) {
          const tasksStore = db.createObjectStore('tasks', { keyPath: 'id' });
          tasksStore.createIndex('user_id', 'user_id', { unique: false });
          tasksStore.createIndex('status', 'status', { unique: false });
          tasksStore.createIndex('updated_at', 'updated_at', { unique: false });
        }
        
        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('action', 'action', { unique: false });
        }
        
        // User data store
        if (!db.objectStoreNames.contains('userData')) {
          db.createObjectStore('userData', { keyPath: 'key' });
        }
        
        // Habits store
        if (!db.objectStoreNames.contains('habits')) {
          const habitsStore = db.createObjectStore('habits', { keyPath: 'id' });
          habitsStore.createIndex('user_id', 'user_id', { unique: false });
        }
        
        // Teams store
        if (!db.objectStoreNames.contains('teams')) {
          const teamsStore = db.createObjectStore('teams', { keyPath: 'id' });
          teamsStore.createIndex('user_id', 'user_id', { unique: false });
        }
      };
    });
  }

  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);
        
        // Listen for messages from service worker
        navigator.serviceWorker.addEventListener('message', (event) => {
          if (event.data.type === 'BACKGROUND_SYNC') {
            this.performBackgroundSync();
          }
        });
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }

  setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.performSync();
      this.notifyNetworkChange('online');
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.notifyNetworkChange('offline');
    });
  }

  notifyNetworkChange(status) {
    window.dispatchEvent(new CustomEvent('networkStatusChange', {
      detail: { isOnline: status === 'online' }
    }));
  }

  // Local storage operations
  async saveTask(task) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readwrite');
    const store = transaction.objectStore('tasks');
    
    const taskWithTimestamp = {
      ...task,
      lastModified: Date.now(),
      offline: !this.isOnline
    };
    
    await store.put(taskWithTimestamp);
    
    // Add to sync queue if offline
    if (!this.isOnline) {
      await this.addToSyncQueue('CREATE_TASK', taskWithTimestamp);
    }
    
    return taskWithTimestamp;
  }

  async updateTask(taskId, updates) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readwrite');
    const store = transaction.objectStore('tasks');
    
    const existingTask = await store.get(taskId);
    if (!existingTask) {
      throw new Error('Task not found');
    }
    
    const updatedTask = {
      ...existingTask,
      ...updates,
      lastModified: Date.now(),
      offline: !this.isOnline
    };
    
    await store.put(updatedTask);
    
    // Add to sync queue if offline
    if (!this.isOnline) {
      await this.addToSyncQueue('UPDATE_TASK', updatedTask);
    }
    
    return updatedTask;
  }

  async deleteTask(taskId) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readwrite');
    const store = transaction.objectStore('tasks');
    
    await store.delete(taskId);
    
    // Add to sync queue if offline
    if (!this.isOnline) {
      await this.addToSyncQueue('DELETE_TASK', { id: taskId });
    }
  }

  async getTasks(userId) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readonly');
    const store = transaction.objectStore('tasks');
    const index = store.index('user_id');
    
    return new Promise((resolve, reject) => {
      const request = index.getAll(userId);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async saveUserData(key, data) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['userData'], 'readwrite');
    const store = transaction.objectStore('userData');
    
    await store.put({ key, data, timestamp: Date.now() });
  }

  async getUserData(key) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['userData'], 'readonly');
    const store = transaction.objectStore('userData');
    
    return new Promise((resolve, reject) => {
      const request = store.get(key);
      request.onsuccess = () => resolve(request.result?.data || null);
      request.onerror = () => reject(request.error);
    });
  }

  // Sync queue management
  async addToSyncQueue(action, data) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    
    const syncItem = {
      action,
      data,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    await store.add(syncItem);
    this.syncQueue.push(syncItem);
  }

  async getSyncQueue() {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['syncQueue'], 'readonly');
    const store = transaction.objectStore('syncQueue');
    
    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async clearSyncQueue() {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    
    await store.clear();
    this.syncQueue = [];
  }

  async removeSyncItem(id) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    
    await store.delete(id);
    this.syncQueue = this.syncQueue.filter(item => item.id !== id);
  }

  // Sync operations
  async performSync() {
    if (this.syncInProgress || !this.isOnline) {
      return;
    }
    
    this.syncInProgress = true;
    
    try {
      const syncQueue = await this.getSyncQueue();
      
      for (const item of syncQueue) {
        try {
          await this.processSyncItem(item);
          await this.removeSyncItem(item.id);
        } catch (error) {
          console.error('Sync item failed:', error);
          // Increment retry count
          item.retryCount = (item.retryCount || 0) + 1;
          
          // Remove from queue if too many retries
          if (item.retryCount > 3) {
            await this.removeSyncItem(item.id);
          }
        }
      }
      
      // Sync data from server
      await this.syncFromServer();
      
      this.notifySyncComplete();
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  async processSyncItem(item) {
    const { action, data } = item;
    
    switch (action) {
      case 'CREATE_TASK':
        await this.syncCreateTask(data);
        break;
      case 'UPDATE_TASK':
        await this.syncUpdateTask(data);
        break;
      case 'DELETE_TASK':
        await this.syncDeleteTask(data);
        break;
      default:
        console.warn('Unknown sync action:', action);
    }
  }

  async syncCreateTask(taskData) {
    const response = await fetch('/api/v1/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(taskData)
    });
    
    if (!response.ok) {
      throw new Error('Failed to sync task creation');
    }
    
    const serverTask = await response.json();
    
    // Update local task with server ID
    await this.updateLocalTask(taskData.id, serverTask);
  }

  async syncUpdateTask(taskData) {
    const response = await fetch(`/api/v1/tasks/${taskData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(taskData)
    });
    
    if (!response.ok) {
      throw new Error('Failed to sync task update');
    }
  }

  async syncDeleteTask(taskData) {
    const response = await fetch(`/api/v1/tasks/${taskData.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (!response.ok && response.status !== 404) {
      throw new Error('Failed to sync task deletion');
    }
  }

  async updateLocalTask(localId, serverTask) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readwrite');
    const store = transaction.objectStore('tasks');
    
    // Remove old task and add new one with server ID
    await store.delete(localId);
    await store.put({ ...serverTask, offline: false });
  }

  async syncFromServer() {
    try {
      const response = await fetch('/api/v1/tasks', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch tasks from server');
      }
      
      const serverTasks = await response.json();
      
      // Update local database with server data
      await this.updateLocalTasks(serverTasks);
    } catch (error) {
      console.error('Failed to sync from server:', error);
    }
  }

  async updateLocalTasks(serverTasks) {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks'], 'readwrite');
    const store = transaction.objectStore('tasks');
    
    for (const task of serverTasks) {
      const existingTask = await store.get(task.id);
      
      // Only update if server version is newer or local doesn't exist
      if (!existingTask || existingTask.lastModified < task.updated_at) {
        await store.put({
          ...task,
          lastModified: new Date(task.updated_at).getTime(),
          offline: false
        });
      }
    }
  }

  async performBackgroundSync() {
    // This method is called by the service worker for background sync
    if (this.isOnline) {
      await this.performSync();
    }
  }

  notifySyncComplete() {
    window.dispatchEvent(new CustomEvent('syncComplete', {
      detail: { timestamp: Date.now() }
    }));
  }

  // Cache management
  async clearCache() {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks', 'syncQueue', 'userData'], 'readwrite');
    
    await Promise.all([
      transaction.objectStore('tasks').clear(),
      transaction.objectStore('syncQueue').clear(),
      transaction.objectStore('userData').clear()
    ]);
    
    this.syncQueue = [];
  }

  async getCacheSize() {
    if (!this.db) await this.initializeDB();
    
    const transaction = this.db.transaction(['tasks', 'syncQueue', 'userData'], 'readonly');
    
    const counts = await Promise.all([
      this.getStoreCount(transaction.objectStore('tasks')),
      this.getStoreCount(transaction.objectStore('syncQueue')),
      this.getStoreCount(transaction.objectStore('userData'))
    ]);
    
    return {
      tasks: counts[0],
      syncQueue: counts[1],
      userData: counts[2],
      total: counts.reduce((sum, count) => sum + count, 0)
    };
  }

  async getStoreCount(store) {
    return new Promise((resolve, reject) => {
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Status methods
  getNetworkStatus() {
    return this.isOnline;
  }

  getSyncStatus() {
    return {
      inProgress: this.syncInProgress,
      queueSize: this.syncQueue.length,
      lastSync: localStorage.getItem('lastSyncTime')
    };
  }
}

// Create singleton instance
const offlineService = new OfflineService();
export default offlineService;