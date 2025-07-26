import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, CheckCircle, Clock, Target, Brain, Heart } from 'lucide-react';
import { useTasks } from '../../contexts/TasksContext';
import { useAuth } from '../../contexts/AuthContext';
import './Analytics.css';

const Analytics = () => {
  const navigate = useNavigate();
  const { tasks } = useTasks();
  const { user } = useAuth();
  
  const [analyticsData, setAnalyticsData] = useState({
    completionRate: 0,
    averageCompletionTime: 0,
    productivityTrend: 'stable',
    mostProductiveTime: 'morning',
    tasksByPriority: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
    completedTasksThisWeek: 0,
    totalTasksThisWeek: 0,
    streakDays: 0
  });

  const [timeRange, setTimeRange] = useState('week'); // week, month, year

  useEffect(() => {
    calculateAnalytics();
  }, [tasks, timeRange]);

  const calculateAnalytics = () => {
    if (!tasks.length) return;

    const now = new Date();
    const timeRanges = {
      week: 7,
      month: 30,
      year: 365
    };

    const daysBack = timeRanges[timeRange];
    const startDate = new Date(now.getTime() - (daysBack * 24 * 60 * 60 * 1000));

    // Filter tasks within time range
    const relevantTasks = tasks.filter(task => {
      const taskDate = new Date(task.created_at);
      return taskDate >= startDate;
    });

    const completedTasks = relevantTasks.filter(task => task.status === 'completed');
    
    // Completion rate
    const completionRate = relevantTasks.length > 0 
      ? Math.round((completedTasks.length / relevantTasks.length) * 100)
      : 0;

    // Average completion time (placeholder calculation)
    const averageCompletionTime = completedTasks.length > 0
      ? Math.round(completedTasks.reduce((acc, task) => {
          if (task.completed_at && task.created_at) {
            const start = new Date(task.created_at);
            const end = new Date(task.completed_at);
            return acc + (end - start) / (1000 * 60 * 60); // hours
          }
          return acc + 24; // default 24 hours if no completion time
        }, 0) / completedTasks.length)
      : 0;

    // Tasks by priority
    const tasksByPriority = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    relevantTasks.forEach(task => {
      tasksByPriority[task.priority] = (tasksByPriority[task.priority] || 0) + 1;
    });

    // This week's stats
    const weekStart = new Date(now);
    weekStart.setDate(now.getDate() - now.getDay());
    weekStart.setHours(0, 0, 0, 0);

    const thisWeekTasks = tasks.filter(task => {
      const taskDate = new Date(task.created_at);
      return taskDate >= weekStart;
    });

    const completedThisWeek = thisWeekTasks.filter(task => task.status === 'completed').length;

    // Calculate streak (consecutive days with completed tasks)
    const streakDays = calculateStreak();

    // Productivity trend (simplified)
    const lastWeekTasks = tasks.filter(task => {
      const taskDate = new Date(task.created_at);
      const lastWeekStart = new Date(weekStart);
      lastWeekStart.setDate(lastWeekStart.getDate() - 7);
      return taskDate >= lastWeekStart && taskDate < weekStart;
    });

    const lastWeekCompleted = lastWeekTasks.filter(task => task.status === 'completed').length;
    const productivityTrend = completedThisWeek > lastWeekCompleted ? 'up' : 
                             completedThisWeek < lastWeekCompleted ? 'down' : 'stable';

    setAnalyticsData({
      completionRate,
      averageCompletionTime,
      productivityTrend,
      mostProductiveTime: 'morning', // Could be calculated from task completion times
      tasksByPriority,
      completedTasksThisWeek: completedThisWeek,
      totalTasksThisWeek: thisWeekTasks.length,
      streakDays
    });
  };

  const calculateStreak = () => {
    // Calculate consecutive days with at least one completed task
    const today = new Date();
    let streak = 0;
    let currentDate = new Date(today);

    while (streak < 365) { // Limit to avoid infinite loop
      const dayStart = new Date(currentDate);
      dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(currentDate);
      dayEnd.setHours(23, 59, 59, 999);

      const dayTasks = tasks.filter(task => {
        const completedDate = task.completed_at ? new Date(task.completed_at) : null;
        return completedDate && completedDate >= dayStart && completedDate <= dayEnd;
      });

      if (dayTasks.length > 0) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }

    return streak;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      1: '#d1d5db',
      2: '#60a5fa',
      3: '#34d399',
      4: '#fbbf24',
      5: '#f87171'
    };
    return colors[priority] || '#d1d5db';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp size={20} className="trend-up" />;
    if (trend === 'down') return <TrendingUp size={20} className="trend-down" />;
    return <TrendingUp size={20} className="trend-stable" />;
  };

  return (
    <div className="analytics-view">
      {/* Header */}
      <div className="analytics-header">
        <button 
          onClick={() => navigate('/main')}
          className="back-button"
          aria-label="Back to main app"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        <h1>Analytics & Insights</h1>
        
        <div className="time-range-selector">
          {['week', 'month', 'year'].map(range => (
            <button
              key={range}
              className={`range-button ${timeRange === range ? 'active' : ''}`}
              onClick={() => setTimeRange(range)}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="analytics-content">
        {/* Key Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">
              <CheckCircle size={24} />
            </div>
            <div className="metric-content">
              <h3>Completion Rate</h3>
              <div className="metric-value">{analyticsData.completionRate}%</div>
              <div className="metric-trend">
                {getTrendIcon(analyticsData.productivityTrend)}
                <span>{analyticsData.productivityTrend === 'up' ? 'Improving' : 
                       analyticsData.productivityTrend === 'down' ? 'Declining' : 'Stable'}</span>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <Clock size={24} />
            </div>
            <div className="metric-content">
              <h3>Avg. Completion Time</h3>
              <div className="metric-value">{analyticsData.averageCompletionTime}h</div>
              <div className="metric-subtitle">Per task</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <Target size={24} />
            </div>
            <div className="metric-content">
              <h3>This Week</h3>
              <div className="metric-value">
                {analyticsData.completedTasksThisWeek}/{analyticsData.totalTasksThisWeek}
              </div>
              <div className="metric-subtitle">Tasks completed</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <Brain size={24} />
            </div>
            <div className="metric-content">
              <h3>Current Streak</h3>
              <div className="metric-value">{analyticsData.streakDays}</div>
              <div className="metric-subtitle">Days active</div>
            </div>
          </div>
        </div>

        {/* Priority Distribution */}
        <div className="chart-section">
          <h2>Tasks by Priority</h2>
          <div className="priority-chart">
            {Object.entries(analyticsData.tasksByPriority).map(([priority, count]) => (
              <div key={priority} className="priority-bar">
                <div className="priority-label">P{priority}</div>
                <div className="priority-bar-container">
                  <div 
                    className="priority-bar-fill"
                    style={{ 
                      width: `${count > 0 ? (count / Math.max(...Object.values(analyticsData.tasksByPriority))) * 100 : 0}%`,
                      backgroundColor: getPriorityColor(parseInt(priority))
                    }}
                  />
                </div>
                <div className="priority-count">{count}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights */}
        <div className="insights-section">
          <h2>AI Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <div className="insight-icon">
                <TrendingUp size={20} />
              </div>
              <div className="insight-content">
                <h4>Productivity Pattern</h4>
                <p>You tend to be most productive in the {analyticsData.mostProductiveTime}. 
                   Consider scheduling high-priority tasks during this time.</p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">
                <Heart size={20} />
              </div>
              <div className="insight-content">
                <h4>Work-Life Balance</h4>
                <p>
                  {analyticsData.completionRate > 80 
                    ? "Great job maintaining productivity! Don't forget to take breaks."
                    : analyticsData.completionRate > 60
                    ? "You're doing well! Consider breaking larger tasks into smaller ones."
                    : "Focus on completing fewer tasks well rather than taking on too many."
                  }
                </p>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon">
                <Target size={20} />
              </div>
              <div className="insight-content">
                <h4>Goal Recommendation</h4>
                <p>
                  {analyticsData.streakDays >= 7
                    ? `Amazing ${analyticsData.streakDays}-day streak! Keep it up!`
                    : analyticsData.streakDays >= 3
                    ? "You're building a good habit. Try to extend your streak!"
                    : "Start with completing just one task daily to build momentum."
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;