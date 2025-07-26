import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Clock, 
  Zap, 
  Target, 
  TrendingUp, 
  BarChart3,
  RefreshCw,
  Settings,
  Star,
  AlertCircle,
  CheckCircle,
  ArrowRight
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './AIScheduling.css';

const AIScheduling = () => {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [activeTab, setActiveTab] = useState('schedule');

  useEffect(() => {
    fetchSchedule();
    fetchAnalytics();
    fetchSuggestions();
  }, [selectedDate]);

  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const response = await api.post('/scheduling/optimize', {
        target_date: selectedDate
      });
      setSchedule(response.data);
    } catch (error) {
      console.error('Failed to fetch schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/scheduling/analytics');
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await api.get(`/scheduling/suggestions?date=${selectedDate}`);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const handleOptimizeSchedule = async () => {
    await fetchSchedule();
  };

  const formatTime = (timeString) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getEnergyColor = (energyLevel) => {
    switch (energyLevel) {
      case 'high': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'low': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'work': return <Target size={16} />;
      case 'personal': return <Star size={16} />;
      case 'fitness': return <Zap size={16} />;
      case 'habit': return <CheckCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const renderScheduleView = () => (
    <div className="schedule-view">
      <div className="schedule-header">
        <div className="schedule-controls">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="date-input"
          />
          <button 
            className="optimize-btn"
            onClick={handleOptimizeSchedule}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            {loading ? 'Optimizing...' : 'Optimize'}
          </button>
        </div>

        {schedule?.metrics && (
          <div className="schedule-metrics">
            <div className="metric">
              <span className="metric-label">Optimization Score</span>
              <span className="metric-value">{schedule.metrics.optimization_score}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Work-Life Balance</span>
              <span className="metric-value">
                {Math.round(schedule.metrics.work_life_balance.work_percentage)}% / {Math.round(schedule.metrics.work_life_balance.personal_percentage)}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Scheduled Items</span>
              <span className="metric-value">{schedule.metrics.total_scheduled_items}</span>
            </div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="loading-state">
          <RefreshCw className="spinning" size={24} />
          <p>Creating your optimized schedule...</p>
        </div>
      ) : schedule?.schedule?.schedule_blocks ? (
        <div className="schedule-timeline">
          {schedule.schedule.schedule_blocks.map((block, index) => (
            <div key={index} className="schedule-block">
              <div className="block-time">
                <span className="start-time">{formatTime(block.start_time)}</span>
                <span className="end-time">{formatTime(block.end_time)}</span>
              </div>
              <div className="block-content">
                <div className="block-header">
                  <div className="block-icon">
                    {getTypeIcon(block.type)}
                  </div>
                  <h3 className="block-title">{block.title}</h3>
                  <div 
                    className="energy-indicator"
                    style={{ backgroundColor: getEnergyColor(block.energy_match) }}
                    title={`${block.energy_match} energy match`}
                  />
                </div>
                <div className="block-meta">
                  <span className="block-type">{block.type}</span>
                  <span className="block-duration">
                    {Math.round((new Date(`2000-01-01T${block.end_time}`) - new Date(`2000-01-01T${block.start_time}`)) / 60000)} min
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-schedule">
          <Calendar size={48} />
          <h3>No schedule generated yet</h3>
          <p>Click "Optimize" to create your AI-powered daily schedule</p>
        </div>
      )}

      {schedule?.recommendations && schedule.recommendations.length > 0 && (
        <div className="recommendations">
          <h3>Recommendations</h3>
          <div className="recommendation-list">
            {schedule.recommendations.map((rec, index) => (
              <div key={index} className={`recommendation ${rec.priority}`}>
                <AlertCircle size={16} />
                <div className="recommendation-content">
                  <h4>{rec.title}</h4>
                  <p>{rec.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {schedule?.schedule?.unscheduled_tasks && schedule.schedule.unscheduled_tasks.length > 0 && (
        <div className="unscheduled-tasks">
          <h3>Unscheduled Tasks</h3>
          <div className="task-list">
            {schedule.schedule.unscheduled_tasks.map((task, index) => (
              <div key={index} className="unscheduled-task">
                <h4>{task.title}</h4>
                <div className="task-meta">
                  <span>Priority: {task.priority}</span>
                  <span>Est. {task.estimated_duration}min</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="analytics-view">
      {analytics ? (
        <>
          <div className="analytics-overview">
            <div className="overview-cards">
              <div className="overview-card">
                <div className="card-icon">
                  <TrendingUp size={24} />
                </div>
                <div className="card-content">
                  <h3>Avg. Optimization</h3>
                  <span className="card-value">{analytics.average_optimization_score}%</span>
                </div>
              </div>
              <div className="overview-card">
                <div className="card-icon">
                  <CheckCircle size={24} />
                </div>
                <div className="card-content">
                  <h3>Completion Rate</h3>
                  <span className="card-value">{analytics.completion_rate}%</span>
                </div>
              </div>
              <div className="overview-card">
                <div className="card-icon">
                  <BarChart3 size={24} />
                </div>
                <div className="card-content">
                  <h3>Schedules Generated</h3>
                  <span className="card-value">{analytics.total_schedules_generated}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="productivity-trends">
            <h3>Productivity Trends</h3>
            <div className="trend-grid">
              {Object.entries(analytics.productivity_trends).map(([time, data]) => (
                <div key={time} className="trend-item">
                  <h4>{time.charAt(0).toUpperCase() + time.slice(1)}</h4>
                  <div className="trend-score">{data.score}%</div>
                  <div className={`trend-indicator ${data.trend}`}>
                    <ArrowRight size={12} />
                    {data.trend}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="task-distribution">
            <h3>Task Category Distribution</h3>
            <div className="distribution-chart">
              {Object.entries(analytics.task_category_distribution).map(([category, percentage]) => (
                <div key={category} className="distribution-item">
                  <span className="category-name">{category}</span>
                  <div className="percentage-bar">
                    <div 
                      className="percentage-fill"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="percentage-value">{percentage}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="weekly-patterns">
            <h3>Weekly Patterns</h3>
            <div className="pattern-grid">
              {Object.entries(analytics.weekly_patterns).map(([day, data]) => (
                <div key={day} className="pattern-item">
                  <h4>{day.charAt(0).toUpperCase() + day.slice(1)}</h4>
                  <div className={`energy-level ${data.energy}`}>
                    Energy: {data.energy}
                  </div>
                  <div className="productivity-score">
                    {data.productivity}% productive
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="ai-insights">
            <h3>AI Insights</h3>
            <div className="insights-list">
              {analytics.insights.map((insight, index) => (
                <div key={index} className="insight-item">
                  <div className="insight-header">
                    <h4>{insight.title}</h4>
                    <div className="confidence-score">
                      {Math.round(insight.confidence * 100)}% confident
                    </div>
                  </div>
                  <p>{insight.message}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="loading-state">
          <RefreshCw className="spinning" size={24} />
          <p>Loading analytics...</p>
        </div>
      )}
    </div>
  );

  const renderSuggestionsView = () => (
    <div className="suggestions-view">
      <h3>Smart Suggestions</h3>
      {suggestions.length > 0 ? (
        <div className="suggestions-list">
          {suggestions.map((suggestion, index) => (
            <div key={index} className={`suggestion-item ${suggestion.priority}`}>
              <div className="suggestion-header">
                <div className="suggestion-icon">
                  {suggestion.type === 'productivity' && <Zap size={20} />}
                  {suggestion.type === 'balance' && <Target size={20} />}
                  {suggestion.type === 'health' && <Star size={20} />}
                  {suggestion.type === 'optimization' && <TrendingUp size={20} />}
                </div>
                <h4>{suggestion.title}</h4>
                <span className={`priority-badge ${suggestion.priority}`}>
                  {suggestion.priority}
                </span>
              </div>
              <p>{suggestion.message}</p>
              {suggestion.actionable && (
                <button className="apply-suggestion-btn">
                  Apply Suggestion
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-suggestions">
          <Settings size={48} />
          <h4>No suggestions available</h4>
          <p>Generate a schedule first to receive personalized suggestions</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="ai-scheduling">
      <div className="scheduling-header">
        <div className="header-content">
          <h1>AI-Powered Scheduling</h1>
          <p>Let AI optimize your daily schedule for maximum productivity and balance</p>
        </div>
      </div>

      <div className="scheduling-tabs">
        <button 
          className={`tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          <Calendar size={16} />
          Schedule
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart3 size={16} />
          Analytics
        </button>
        <button 
          className={`tab ${activeTab === 'suggestions' ? 'active' : ''}`}
          onClick={() => setActiveTab('suggestions')}
        >
          <Star size={16} />
          Suggestions
        </button>
      </div>

      <div className="scheduling-content">
        {activeTab === 'schedule' && renderScheduleView()}
        {activeTab === 'analytics' && renderAnalyticsView()}
        {activeTab === 'suggestions' && renderSuggestionsView()}
      </div>
    </div>
  );
};

export default AIScheduling;