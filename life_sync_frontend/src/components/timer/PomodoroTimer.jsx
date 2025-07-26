import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Settings, 
  Coffee, 
  Brain,
  Target,
  BarChart3,
  Volume2,
  VolumeX
} from 'lucide-react';
import './PomodoroTimer.css';

const PomodoroTimer = ({ taskId = null, onSessionComplete = null }) => {
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isActive, setIsActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('work'); // work, shortBreak, longBreak
  const [sessionsCompleted, setSessionsCompleted] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  
  const [settings, setSettings] = useState({
    workDuration: 25,
    shortBreakDuration: 5,
    longBreakDuration: 15,
    sessionsUntilLongBreak: 4,
    autoStartBreaks: false,
    autoStartWork: false,
    notifications: true
  });

  const [todayStats, setTodayStats] = useState({
    totalSessions: 0,
    totalWorkTime: 0,
    totalBreakTime: 0,
    focusScore: 0
  });

  const intervalRef = useRef(null);
  const audioRef = useRef(null);

  // Initialize timer based on current phase
  useEffect(() => {
    const duration = getCurrentPhaseDuration();
    setTimeLeft(duration * 60);
  }, [currentPhase, settings]);

  // Timer logic
  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handlePhaseComplete();
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isActive, timeLeft]);

  // Load stats from localStorage on mount
  useEffect(() => {
    const savedStats = localStorage.getItem('pomodoroStats');
    if (savedStats) {
      const stats = JSON.parse(savedStats);
      const today = new Date().toDateString();
      if (stats.date === today) {
        setTodayStats(stats);
      }
    }
  }, []);

  const getCurrentPhaseDuration = () => {
    switch (currentPhase) {
      case 'work':
        return settings.workDuration;
      case 'shortBreak':
        return settings.shortBreakDuration;
      case 'longBreak':
        return settings.longBreakDuration;
      default:
        return settings.workDuration;
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    const totalTime = getCurrentPhaseDuration() * 60;
    return ((totalTime - timeLeft) / totalTime) * 100;
  };

  const handleStart = () => {
    setIsActive(true);
  };

  const handlePause = () => {
    setIsActive(false);
  };

  const handleStop = () => {
    setIsActive(false);
    setTimeLeft(getCurrentPhaseDuration() * 60);
  };

  const handleReset = () => {
    setIsActive(false);
    setTimeLeft(getCurrentPhaseDuration() * 60);
    setSessionsCompleted(0);
    setCurrentPhase('work');
  };

  const handlePhaseComplete = () => {
    setIsActive(false);
    playNotificationSound();
    showNotification();
    updateStats();

    if (currentPhase === 'work') {
      const newSessionsCompleted = sessionsCompleted + 1;
      setSessionsCompleted(newSessionsCompleted);
      
      // Determine next phase
      if (newSessionsCompleted % settings.sessionsUntilLongBreak === 0) {
        setCurrentPhase('longBreak');
      } else {
        setCurrentPhase('shortBreak');
      }

      // Call callback if provided
      if (onSessionComplete) {
        onSessionComplete({
          taskId,
          duration: settings.workDuration,
          completedAt: new Date(),
          sessionsCompleted: newSessionsCompleted
        });
      }

      // Auto-start break if enabled
      if (settings.autoStartBreaks) {
        setTimeout(() => setIsActive(true), 1000);
      }
    } else {
      // Break completed, return to work
      setCurrentPhase('work');
      
      if (settings.autoStartWork) {
        setTimeout(() => setIsActive(true), 1000);
      }
    }
  };

  const playNotificationSound = () => {
    if (soundEnabled && audioRef.current) {
      audioRef.current.play().catch(e => console.log('Audio play failed:', e));
    }
  };

  const showNotification = () => {
    if (settings.notifications && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        const title = currentPhase === 'work' ? 'Work Session Complete!' : 'Break Time Over!';
        const body = currentPhase === 'work' 
          ? 'Great focus! Time for a break.' 
          : 'Break time is over. Ready to focus?';
        
        new Notification(title, {
          body,
          icon: '/images/LifeSyncLogo.png',
          tag: 'pomodoro'
        });
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission();
      }
    }
  };

  const updateStats = () => {
    const today = new Date().toDateString();
    const sessionDuration = getCurrentPhaseDuration();
    
    setTodayStats(prevStats => {
      const newStats = { ...prevStats, date: today };
      
      if (currentPhase === 'work') {
        newStats.totalSessions += 1;
        newStats.totalWorkTime += sessionDuration;
        newStats.focusScore = Math.min(100, newStats.totalSessions * 5);
      } else {
        newStats.totalBreakTime += sessionDuration;
      }
      
      // Save to localStorage
      localStorage.setItem('pomodoroStats', JSON.stringify(newStats));
      return newStats;
    });
  };

  const getPhaseColor = () => {
    switch (currentPhase) {
      case 'work':
        return '#ef4444'; // Red
      case 'shortBreak':
        return '#10b981'; // Green
      case 'longBreak':
        return '#3b82f6'; // Blue
      default:
        return '#ef4444';
    }
  };

  const getPhaseIcon = () => {
    switch (currentPhase) {
      case 'work':
        return <Brain size={24} />;
      case 'shortBreak':
        return <Coffee size={24} />;
      case 'longBreak':
        return <Coffee size={24} />;
      default:
        return <Brain size={24} />;
    }
  };

  const getPhaseLabel = () => {
    switch (currentPhase) {
      case 'work':
        return 'Focus Time';
      case 'shortBreak':
        return 'Short Break';
      case 'longBreak':
        return 'Long Break';
      default:
        return 'Focus Time';
    }
  };

  return (
    <div className="pomodoro-timer">
      <audio ref={audioRef} preload="auto">
        <source src="/sounds/notification.mp3" type="audio/mpeg" />
        <source src="/sounds/notification.wav" type="audio/wav" />
      </audio>

      <div className="timer-header">
        <div className="phase-info">
          <div className="phase-icon" style={{ color: getPhaseColor() }}>
            {getPhaseIcon()}
          </div>
          <div className="phase-details">
            <h3 className="phase-label">{getPhaseLabel()}</h3>
            <span className="sessions-count">Session {sessionsCompleted + 1}</span>
          </div>
        </div>
        <div className="timer-actions">
          <button
            className="action-btn"
            onClick={() => setSoundEnabled(!soundEnabled)}
            title={soundEnabled ? 'Mute' : 'Unmute'}
          >
            {soundEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
          </button>
          <button
            className="action-btn"
            onClick={() => setShowSettings(true)}
            title="Settings"
          >
            <Settings size={18} />
          </button>
        </div>
      </div>

      <div className="timer-display">
        <div 
          className="timer-circle"
          style={{ 
            background: `conic-gradient(${getPhaseColor()} ${getProgressPercentage() * 3.6}deg, var(--color-secondary) 0deg)`
          }}
        >
          <div className="timer-inner">
            <div className="time-text">{formatTime(timeLeft)}</div>
            <div className="timer-progress-text">
              {Math.round(getProgressPercentage())}% complete
            </div>
          </div>
        </div>
      </div>

      <div className="timer-controls">
        {!isActive ? (
          <button className="control-btn primary" onClick={handleStart}>
            <Play size={24} />
            Start
          </button>
        ) : (
          <button className="control-btn secondary" onClick={handlePause}>
            <Pause size={24} />
            Pause
          </button>
        )}
        <button className="control-btn secondary" onClick={handleStop}>
          <Square size={20} />
          Stop
        </button>
        <button className="control-btn secondary" onClick={handleReset}>
          <RotateCcw size={20} />
          Reset
        </button>
      </div>

      <div className="today-stats">
        <h4>Today's Progress</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <Target size={16} />
            <span className="stat-value">{todayStats.totalSessions}</span>
            <span className="stat-label">Sessions</span>
          </div>
          <div className="stat-item">
            <Brain size={16} />
            <span className="stat-value">{todayStats.totalWorkTime}m</span>
            <span className="stat-label">Focus Time</span>
          </div>
          <div className="stat-item">
            <Coffee size={16} />
            <span className="stat-value">{todayStats.totalBreakTime}m</span>
            <span className="stat-label">Break Time</span>
          </div>
          <div className="stat-item">
            <BarChart3 size={16} />
            <span className="stat-value">{todayStats.focusScore}</span>
            <span className="stat-label">Focus Score</span>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay">
          <div className="modal timer-settings-modal">
            <div className="modal-header">
              <h3>Timer Settings</h3>
              <button 
                className="close-btn"
                onClick={() => setShowSettings(false)}
              >
                ×
              </button>
            </div>
            <div className="settings-content">
              <div className="settings-group">
                <h4>Duration Settings</h4>
                <div className="setting-item">
                  <label>Work Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={settings.workDuration}
                    onChange={(e) => setSettings({
                      ...settings,
                      workDuration: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div className="setting-item">
                  <label>Short Break Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={settings.shortBreakDuration}
                    onChange={(e) => setSettings({
                      ...settings,
                      shortBreakDuration: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div className="setting-item">
                  <label>Long Break Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={settings.longBreakDuration}
                    onChange={(e) => setSettings({
                      ...settings,
                      longBreakDuration: parseInt(e.target.value)
                    })}
                  />
                </div>
                <div className="setting-item">
                  <label>Sessions Until Long Break</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={settings.sessionsUntilLongBreak}
                    onChange={(e) => setSettings({
                      ...settings,
                      sessionsUntilLongBreak: parseInt(e.target.value)
                    })}
                  />
                </div>
              </div>

              <div className="settings-group">
                <h4>Automation</h4>
                <div className="setting-item checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.autoStartBreaks}
                      onChange={(e) => setSettings({
                        ...settings,
                        autoStartBreaks: e.target.checked
                      })}
                    />
                    Auto-start breaks
                  </label>
                </div>
                <div className="setting-item checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.autoStartWork}
                      onChange={(e) => setSettings({
                        ...settings,
                        autoStartWork: e.target.checked
                      })}
                    />
                    Auto-start work sessions
                  </label>
                </div>
                <div className="setting-item checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.notifications}
                      onChange={(e) => setSettings({
                        ...settings,
                        notifications: e.target.checked
                      })}
                    />
                    Enable notifications
                  </label>
                </div>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                onClick={() => setShowSettings(false)}
                className="save-settings-btn"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PomodoroTimer;