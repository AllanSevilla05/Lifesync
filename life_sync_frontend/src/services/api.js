const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getToken() {
    return localStorage.getItem('access_token');
  }

  setToken(token) {
    localStorage.setItem('access_token', token);
  }

  removeToken() {
    localStorage.removeItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Network error' }));
        
        // Handle different error formats
        let errorMessage;
        
        if (error.detail) {
          // Standard FastAPI error with detail
          if (Array.isArray(error.detail)) {
            // Pydantic validation errors
            errorMessage = error.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
          } else if (typeof error.detail === 'string') {
            errorMessage = error.detail;
          } else {
            errorMessage = JSON.stringify(error.detail);
          }
        } else if (Array.isArray(error)) {
          // Direct array of Pydantic validation errors
          errorMessage = error.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
        } else {
          errorMessage = `HTTP error! status: ${response.status}`;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: {
        email: userData.email,
        username: userData.email.split('@')[0], // Use email prefix as username
        full_name: `${userData.firstName} ${userData.lastName}`,
        password: userData.password,
      },
    });
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: {
        username: credentials.email,
        password: credentials.password,
      },
    });

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  async logout() {
    this.removeToken();
  }

  // Task endpoints
  async getTasks(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/tasks/?${queryString}` : '/tasks/';
    return this.request(endpoint);
  }

  async createTask(taskData) {
    return this.request('/tasks/', {
      method: 'POST',
      body: taskData,
    });
  }

  async updateTask(taskId, taskData) {
    return this.request(`/tasks/${taskId}`, {
      method: 'PUT',
      body: taskData,
    });
  }

  async deleteTask(taskId) {
    return this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async getTask(taskId) {
    return this.request(`/tasks/${taskId}`);
  }

  async createTasksFromVoice(voiceData) {
    return this.request('/tasks/voice', {
      method: 'POST',
      body: voiceData,
    });
  }

  async taskCheckIn(taskId, checkInData) {
    return this.request(`/tasks/${taskId}/check-in`, {
      method: 'POST',
      body: checkInData,
    });
  }

  async getOptimizedSchedule() {
    return this.request('/tasks/optimize/schedule');
  }
}

export default new ApiService();