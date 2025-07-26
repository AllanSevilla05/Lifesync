import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Play, 
  Pause, 
  Square, 
  Plus, 
  BarChart3, 
  Calendar,
  Target,
  Timer,
  Zap,
  TrendingUp,
  Filter
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTasks } from '../../contexts/TasksContext';
import PomodoroTimer from '../../components/timer/PomodoroTimer';
import api from '../../services/api';
import './TimeTracking.css';

const TimeTracking = () => {
  const { user } = useAuth();
  const { tasks } = useTasks();
  const [activeTimer, setActiveTimer] = useState(null);
  const [timeEntries, setTimeEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('tracker');
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [showPomodoro, setShowPomodoro] = useState(false);
  const [selectedTask, setSelectedTask] = useState('');
  const [analytics, setAnalytics] = useState(null);

  const [manualEntry, setManualEntry] = useState({
    task_id: '',
    description: '',
    duration: '',
    date: new Date().toISOString().split('T')[0],
    category: 'work'
  });

  const [currentSession, setCurrentSession] = useState({
    task_id: '',
    description: '',
    start_time: null,
    elapsed: 0
  });

  useEffect(() => {
    fetchTimeEntries();
    fetchAnalytics();
  }, []);

  // Update elapsed time for active timer
  useEffect(() => {
    let interval;
    if (activeTimer && currentSession.start_time) {
      interval = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now - currentSession.start_time) / 1000);
        setCurrentSession(prev => ({ ...prev, elapsed }));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeTimer, currentSession.start_time]);

  const fetchTimeEntries = async () => {
    try {
      setLoading(true);
      // Mock data for now - replace with actual API call
      const mockEntries = [
        {
          id: 1,
          task_id: 1,
          task_title: 'Design Homepage',
          description: 'Working on new landing page design',
          duration: 7200, // 2 hours in seconds
          date: '2024-01-15',
          category: 'work',
          created_at: '2024-01-15T10:00:00Z'
        },
        {
          id: 2,
          task_id: 2,
          task_title: 'Code Review',
          description: 'Reviewing pull requests',
          duration: 3600, // 1 hour
          date: '2024-01-15',
          category: 'work',
          created_at: '2024-01-15T14:00:00Z'
        }
      ];
      setTimeEntries(mockEntries);
    } catch (error) {
      console.error('Failed to fetch time entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      // Mock analytics - replace with actual API
      const mockAnalytics = {
        today: {
          total_time: 18000, // 5 hours
          sessions: 6,
          avg_session: 3000, // 50 minutes
          productivity_score: 85
        },
        week: {
          total_time: 144000, // 40 hours
          most_productive_day: 'Tuesday',
          categories: {
            work: 70,
            personal: 20,
            learning: 10
          }
        },
        trends: {
          daily_average: 28800, // 8 hours
          weekly_trend: 'increasing',
          focus_score: 78
        }
      };
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const startTimer = (taskId = '', description = '') => {
    if (activeTimer) {
      stopTimer();
    }

    setActiveTimer(Date.now());
    setCurrentSession({
      task_id: taskId,
      description: description || 'Manual time tracking',
      start_time: new Date(),
      elapsed: 0
    });
  };

  const pauseTimer = () => {
    setActiveTimer(null);
  };

  const resumeTimer = () => {
    if (currentSession.start_time) {
      setActiveTimer(Date.now());
      // Adjust start time to account for elapsed time
      const now = new Date();
      const adjustedStart = new Date(now.getTime() - (currentSession.elapsed * 1000));
      setCurrentSession(prev => ({ ...prev, start_time: adjustedStart }));
    }
  };

  const stopTimer = async () => {
    if (currentSession.start_time) {
      const endTime = new Date();
      const duration = Math.floor((endTime - currentSession.start_time) / 1000);
      
      // Save time entry
      const newEntry = {
        id: Date.now(),
        task_id: currentSession.task_id,
        task_title: getTaskTitle(currentSession.task_id),
        description: currentSession.description,
        duration,
        date: new Date().toISOString().split('T')[0],
        category: 'work',
        created_at: new Date().toISOString()
      };

      setTimeEntries(prev => [newEntry, ...prev]);
      
      // Reset timer
      setActiveTimer(null);
      setCurrentSession({
        task_id: '',
        description: '',
        start_time: null,
        elapsed: 0
      });
    }
  };

  const handleManualEntry = async (e) => {
    e.preventDefault();
    try {
      const duration = parseInt(manualEntry.duration) * 60; // Convert minutes to seconds
      
      const newEntry = {
        id: Date.now(),
        task_id: manualEntry.task_id,
        task_title: getTaskTitle(manualEntry.task_id),
        description: manualEntry.description,
        duration,
        date: manualEntry.date,
        category: manualEntry.category,
        created_at: new Date().toISOString()
      };

      setTimeEntries(prev => [newEntry, ...prev]);
      setManualEntry({
        task_id: '',
        description: '',
        duration: '',
        date: new Date().toISOString().split('T')[0],
        category: 'work'
      });
      setShowManualEntry(false);
    } catch (error) {
      console.error('Failed to add manual entry:', error);
    }
  };

  const handlePomodoroComplete = (sessionData) => {
    const newEntry = {
      id: Date.now(),
      task_id: sessionData.taskId,
      task_title: getTaskTitle(sessionData.taskId),
      description: `Pomodoro session ${sessionData.sessionsCompleted}`,
      duration: sessionData.duration * 60, // Convert minutes to seconds
      date: new Date().toISOString().split('T')[0],
      category: 'work',
      created_at: sessionData.completedAt.toISOString()
    };

    setTimeEntries(prev => [newEntry, ...prev]);
  };

  const getTaskTitle = (taskId) => {
    if (!taskId) return 'No task selected';
    const task = tasks.find(t => t.id === parseInt(taskId));
    return task ? task.title : 'Unknown task';
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const renderTimerTab = () => (
    <div className="timer-section">
      <div className="active-timer-card">
        <div className="timer-header">
          <h3>Current Session</h3>
          <div className="timer-display">
            {formatDuration(currentSession.elapsed)}
          </div>
        </div>

        <div className="timer-controls-section">
          <div className="task-selector">
            <select
              value={selectedTask}
              onChange={(e) => setSelectedTask(e.target.value)}
              disabled={activeTimer}
            >
              <option value="">Select a task (optional)</option>
              {tasks.map(task => (
                <option key={task.id} value={task.id}>
                  {task.title}
                </option>
              ))}
            </select>
          </div>

          <div className="timer-buttons">
            {!activeTimer ? (
              <button 
                className="timer-btn start"
                onClick={() => startTimer(selectedTask, 'Working on selected task')}
              >
                <Play size={20} />
                Start Timer
              </button>
            ) : (
              <>
                <button 
                  className="timer-btn pause"
                  onClick={pauseTimer}
                >
                  <Pause size={20} />
                  Pause
                </button>
                <button 
                  className="timer-btn stop"
                  onClick={stopTimer}
                >
                  <Square size={18} />
                  Stop
                </button>
              </>
            )}
          </div>
        </div>

        {currentSession.description && (
          <div className="current-description">
            <strong>Description:</strong> {currentSession.description}
          </div>
        )}
      </div>

      <div className="timer-options">
        <button 
          className="option-btn"
          onClick={() => setShowPomodoro(!showPomodoro)}
        >
          <Timer size={20} />
          {showPomodoro ? 'Hide' : 'Show'} Pomodoro Timer
        </button>
        <button 
          className="option-btn"
          onClick={() => setShowManualEntry(true)}
        >
          <Plus size={20} />
          Add Manual Entry
        </button>
      </div>

      {showPomodoro && (
        <div className="pomodoro-section">
          <PomodoroTimer 
            taskId={selectedTask}
            onSessionComplete={handlePomodoroComplete}
          />
        </div>
      )}

      <div className="recent-entries">
        <h3>Recent Time Entries</h3>
        {timeEntries.slice(0, 5).map(entry => (
          <div key={entry.id} className="time-entry-card">
            <div className="entry-info">
              <h4>{entry.task_title}</h4>
              <p>{entry.description}</p>
              <div className="entry-meta">
                <span className="duration">{formatTime(entry.duration)}</span>
                <span className="date">{new Date(entry.date).toLocaleDateString()}</span>
                <span className={`category ${entry.category}`}>{entry.category}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="analytics-section">
      <div className="analytics-grid">
        <div className="analytics-card">
          <div className="card-header">
            <Clock size={20} />
            <h3>Today's Summary</h3>
          </div>
          <div className="stats-grid">
            <div className="stat">
              <span className="stat-value">{formatTime(analytics?.today?.total_time || 0)}</span>
              <span className="stat-label">Total Time</span>
            </div>
            <div className="stat">
              <span className="stat-value">{analytics?.today?.sessions || 0}</span>
              <span className="stat-label">Sessions</span>
            </div>
            <div className="stat">
              <span className="stat-value">{formatTime(analytics?.today?.avg_session || 0)}</span>
              <span className="stat-label">Avg Session</span>
            </div>
            <div className="stat">
              <span className="stat-value">{analytics?.today?.productivity_score || 0}%</span>
              <span className="stat-label">Productivity</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <BarChart3 size={20} />
            <h3>This Week</h3>
          </div>
          <div className="week-stats">
            <div className="week-stat">
              <span className="week-label">Total Time</span>
              <span className="week-value">{formatTime(analytics?.week?.total_time || 0)}</span>
            </div>
            <div className="week-stat">
              <span className="week-label">Most Productive</span>
              <span className="week-value">{analytics?.week?.most_productive_day || 'N/A'}</span>
            </div>
          </div>
          <div className="category-breakdown">
            <h4>Time by Category</h4>
            {analytics?.week?.categories && Object.entries(analytics.week.categories).map(([category, percentage]) => (
              <div key={category} className="category-bar">
                <span className="category-name">{category}</span>
                <div className="bar-container">
                  <div 
                    className="bar-fill"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="category-percentage">{percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-header">
            <TrendingUp size={20} />
            <h3>Trends</h3>
          </div>
          <div className="trends-content">
            <div className="trend-item">
              <Zap size={16} />
              <div className="trend-info">
                <span className="trend-label">Daily Average</span>
                <span className="trend-value">{formatTime(analytics?.trends?.daily_average || 0)}</span>
              </div>
            </div>
            <div className="trend-item">
              <Target size={16} />
              <div className="trend-info">
                <span className="trend-label">Focus Score</span>
                <span className="trend-value">{analytics?.trends?.focus_score || 0}%</span>
              </div>
            </div>
            <div className="trend-item">
              <TrendingUp size={16} />
              <div className="trend-info">
                <span className="trend-label">Weekly Trend</span>
                <span className={`trend-value ${analytics?.trends?.weekly_trend}`}>
                  {analytics?.trends?.weekly_trend || 'stable'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="history-section">
      <div className="history-header">
        <h3>Time Tracking History</h3>
        <div className="history-filters">
          <select>
            <option value="all">All Categories</option>
            <option value="work">Work</option>
            <option value="personal">Personal</option>
            <option value="learning">Learning</option>
          </select>
          <input type="date" />
        </div>
      </div>

      <div className="history-list">
        {timeEntries.map(entry => (
          <div key={entry.id} className="history-entry">
            <div className="entry-main">
              <div className="entry-header">
                <h4>{entry.task_title}</h4>
                <span className="entry-duration">{formatTime(entry.duration)}</span>
              </div>
              <p className="entry-description">{entry.description}</p>
              <div className="entry-footer">
                <span className="entry-date">
                  {new Date(entry.created_at).toLocaleString()}
                </span>
                <span className={`entry-category ${entry.category}`}>
                  {entry.category}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="time-tracking">
      <div className="time-tracking-header">
        <div className="header-content">
          <h1>Time Tracking</h1>
          <p>Track your time and boost your productivity</p>
        </div>
      </div>

      <div className="time-tracking-tabs">
        <button 
          className={`tab ${activeTab === 'tracker' ? 'active' : ''}`}
          onClick={() => setActiveTab('tracker')}
        >
          <Clock size={16} />
          Timer
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart3 size={16} />
          Analytics
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <Calendar size={16} />
          History
        </button>
      </div>

      <div className="time-tracking-content">
        {activeTab === 'tracker' && renderTimerTab()}
        {activeTab === 'analytics' && renderAnalyticsTab()}
        {activeTab === 'history' && renderHistoryTab()}
      </div>

      {/* Manual Entry Modal */}
      {showManualEntry && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Add Manual Time Entry</h3>
              <button 
                className="close-btn"
                onClick={() => setShowManualEntry(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleManualEntry}>
              <div className="form-group">
                <label>Task (Optional)</label>
                <select
                  value={manualEntry.task_id}
                  onChange={(e) => setManualEntry({...manualEntry, task_id: e.target.value})}
                >
                  <option value="">No specific task</option>
                  {tasks.map(task => (
                    <option key={task.id} value={task.id}>
                      {task.title}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={manualEntry.description}
                  onChange={(e) => setManualEntry({...manualEntry, description: e.target.value})}
                  placeholder="What did you work on?"
                  required
                />
              </div>
              <div className="form-group">
                <label>Duration (minutes)</label>
                <input
                  type="number"
                  value={manualEntry.duration}
                  onChange={(e) => setManualEntry({...manualEntry, duration: e.target.value})}
                  placeholder="120"
                  min="1"
                  required
                />
              </div>
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  value={manualEntry.date}
                  onChange={(e) => setManualEntry({...manualEntry, date: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select
                  value={manualEntry.category}
                  onChange={(e) => setManualEntry({...manualEntry, category: e.target.value})}
                >
                  <option value="work">Work</option>
                  <option value="personal">Personal</option>
                  <option value="learning">Learning</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowManualEntry(false)}>
                  Cancel
                </button>
                <button type="submit" className="add-entry-btn">
                  Add Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeTracking;