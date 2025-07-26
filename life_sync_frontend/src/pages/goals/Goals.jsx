import React, { useState, useEffect } from 'react';
import { 
  Target, 
  Plus, 
  Calendar, 
  TrendingUp, 
  CheckCircle, 
  Clock, 
  Star,
  BarChart3,
  Edit,
  Trash2,
  Eye,
  Award,
  Lightbulb,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Goals.css';

const Goals = () => {
  const { user } = useAuth();
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    goal_type: 'personal',
    priority: 'medium',
    target_value: '',
    unit: '',
    target_date: '',
    time_frame: 'monthly',
    tags: []
  });

  useEffect(() => {
    fetchGoals();
    fetchAnalytics();
    fetchRecommendations();
  }, [activeTab]);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const params = activeTab !== 'all' ? `?status=${activeTab}` : '';
      const response = await api.get(`/goals${params}`);
      setGoals(response.data.goals);
    } catch (error) {
      console.error('Failed to fetch goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/goals/analytics/overview');
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/goals/recommendations/personalized');
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    try {
      const goalData = {
        ...newGoal,
        target_value: newGoal.target_value ? parseFloat(newGoal.target_value) : null,
        target_date: newGoal.target_date ? new Date(newGoal.target_date).toISOString() : null,
        tags: newGoal.tags.filter(tag => tag.trim() !== '')
      };

      const response = await api.post('/goals', goalData);
      
      if (response.data.success) {
        setGoals([response.data.goal, ...goals]);
        setNewGoal({
          title: '',
          description: '',
          goal_type: 'personal',
          priority: 'medium',
          target_value: '',
          unit: '',
          target_date: '',
          time_frame: 'monthly',
          tags: []
        });
        setShowCreateModal(false);
      }
    } catch (error) {
      console.error('Failed to create goal:', error);
      alert('Failed to create goal');
    }
  };

  const handleUpdateProgress = async (goalId, progressValue) => {
    try {
      const response = await api.post(`/goals/${goalId}/progress`, {
        progress_value: parseFloat(progressValue),
        notes: 'Manual progress update'
      });
      
      if (response.data.success) {
        // Update the goal in the list
        setGoals(goals.map(goal => 
          goal.id === goalId 
            ? { ...goal, ...response.data.progress }
            : goal
        ));
      }
    } catch (error) {
      console.error('Failed to update progress:', error);
      alert('Failed to update progress');
    }
  };

  const handleUpdateStatus = async (goalId, newStatus) => {
    try {
      const response = await api.put(`/goals/${goalId}/status`, {
        status: newStatus
      });
      
      if (response.data.success) {
        await fetchGoals(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#10b981';
      case 'completed': return '#059669';
      case 'paused': return '#f59e0b';
      case 'cancelled': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#d97706';
      case 'low': return '#65a30d';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderGoalCard = (goal) => (
    <div key={goal.id} className="goal-card">
      <div className="goal-header">
        <div className="goal-title-section">
          <h3 className="goal-title">{goal.title}</h3>
          <div className="goal-badges">
            <span 
              className="status-badge"
              style={{ backgroundColor: getStatusColor(goal.status) }}
            >
              {goal.status}
            </span>
            <span 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(goal.priority) }}
            >
              {goal.priority}
            </span>
            <span className="type-badge">{goal.goal_type}</span>
          </div>
        </div>
        <div className="goal-actions">
          <button 
            className="action-btn"
            onClick={() => setSelectedGoal(goal)}
            title="View details"
          >
            <Eye size={16} />
          </button>
        </div>
      </div>

      {goal.description && (
        <p className="goal-description">{goal.description}</p>
      )}

      <div className="goal-progress">
        <div className="progress-header">
          <span className="progress-label">Progress</span>
          <span className="progress-value">
            {goal.completion_percentage?.toFixed(1) || 0}%
          </span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${goal.completion_percentage || 0}%` }}
          />
        </div>
        {goal.target_value && (
          <div className="progress-details">
            <span>{goal.current_value || 0} / {goal.target_value} {goal.unit}</span>
          </div>
        )}
      </div>

      <div className="goal-meta">
        <div className="meta-item">
          <Calendar size={14} />
          <span>Due: {formatDate(goal.target_date)}</span>
        </div>
        {goal.difficulty_score && (
          <div className="meta-item">
            <Star size={14} />
            <span>Difficulty: {goal.difficulty_score}/10</span>
          </div>
        )}
      </div>

      {goal.status === 'active' && (
        <div className="goal-quick-actions">
          <input
            type="number"
            placeholder="Update progress"
            className="progress-input"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value) {
                handleUpdateProgress(goal.id, e.target.value);
                e.target.value = '';
              }
            }}
          />
          <button
            className="complete-btn"
            onClick={() => handleUpdateStatus(goal.id, 'completed')}
          >
            <CheckCircle size={16} />
            Complete
          </button>
        </div>
      )}

      {goal.smart_analysis && (
        <div className="smart-score">
          <span className="smart-label">SMART Score:</span>
          <span className="smart-value">{goal.smart_analysis.overall_score}/10</span>
        </div>
      )}
    </div>
  );

  const renderAnalytics = () => (
    <div className="analytics-section">
      <h3>Goal Analytics</h3>
      {analytics ? (
        <div className="analytics-grid">
          <div className="analytics-card">
            <div className="card-header">
              <Target size={20} />
              <h4>Overview</h4>
            </div>
            <div className="stats-grid">
              <div className="stat">
                <span className="stat-value">{analytics.overview.total_goals}</span>
                <span className="stat-label">Total Goals</span>
              </div>
              <div className="stat">
                <span className="stat-value">{analytics.overview.active_goals}</span>
                <span className="stat-label">Active</span>
              </div>
              <div className="stat">
                <span className="stat-value">{analytics.overview.completed_goals}</span>
                <span className="stat-label">Completed</span>
              </div>
              <div className="stat">
                <span className="stat-value">{analytics.overview.completion_rate.toFixed(1)}%</span>
                <span className="stat-label">Success Rate</span>
              </div>
            </div>
          </div>

          <div className="analytics-card">
            <div className="card-header">
              <BarChart3 size={20} />
              <h4>Goal Types</h4>
            </div>
            <div className="goal-types-chart">
              {Object.entries(analytics.goal_types).map(([type, data]) => (
                <div key={type} className="type-stat">
                  <span className="type-name">{type}</span>
                  <div className="type-progress">
                    <div 
                      className="type-progress-fill"
                      style={{ width: `${data.completion_rate}%` }}
                    />
                  </div>
                  <span className="type-rate">{data.completion_rate.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="loading">Loading analytics...</div>
      )}
    </div>
  );

  const renderRecommendations = () => (
    <div className="recommendations-section">
      <h3>AI Recommendations</h3>
      {recommendations.length > 0 ? (
        <div className="recommendations-list">
          {recommendations.map((rec, index) => (
            <div key={index} className="recommendation-card">
              <div className="rec-header">
                <Lightbulb size={18} />
                <h4>{rec.title}</h4>
                <span className="confidence">
                  {Math.round(rec.confidence * 100)}% confident
                </span>
              </div>
              <p>{rec.description}</p>
              <div className="rec-meta">
                <span className="rec-type">{rec.type}</span>
                {rec.suggested_goal_type && (
                  <span className="suggested-type">
                    Suggested: {rec.suggested_goal_type}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-recommendations">
          <Lightbulb size={48} />
          <p>No recommendations available</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="goals-container">
      <div className="goals-header">
        <div className="header-content">
          <h1>Smart Goals</h1>
          <p>Set, track, and achieve your goals with AI assistance</p>
        </div>
        <div className="header-actions">
          <button 
            className="create-goal-btn"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus size={16} />
            Create Goal
          </button>
        </div>
      </div>

      <div className="goals-tabs">
        <button 
          className={`tab ${activeTab === 'active' ? 'active' : ''}`}
          onClick={() => setActiveTab('active')}
        >
          Active Goals
        </button>
        <button 
          className={`tab ${activeTab === 'completed' ? 'active' : ''}`}
          onClick={() => setActiveTab('completed')}
        >
          Completed
        </button>
        <button 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          All Goals
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </div>

      <div className="goals-content">
        {activeTab === 'analytics' ? (
          <div className="analytics-view">
            {renderAnalytics()}
            {renderRecommendations()}
          </div>
        ) : (
          <div className="goals-grid">
            {loading ? (
              <div className="loading">Loading goals...</div>
            ) : goals.length > 0 ? (
              goals.map(renderGoalCard)
            ) : (
              <div className="empty-goals">
                <Target size={48} />
                <h3>No goals found</h3>
                <p>Create your first SMART goal to get started</p>
                <button 
                  className="create-goal-btn"
                  onClick={() => setShowCreateModal(true)}
                >
                  <Plus size={16} />
                  Create Goal
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Goal Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal create-goal-modal">
            <div className="modal-header">
              <h3>Create Smart Goal</h3>
              <button 
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleCreateGoal}>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>Goal Title *</label>
                  <input
                    type="text"
                    value={newGoal.title}
                    onChange={(e) => setNewGoal({...newGoal, title: e.target.value})}
                    placeholder="e.g., Read 12 books this year"
                    required
                  />
                </div>

                <div className="form-group full-width">
                  <label>Description</label>
                  <textarea
                    value={newGoal.description}
                    onChange={(e) => setNewGoal({...newGoal, description: e.target.value})}
                    placeholder="Describe your goal in detail..."
                    rows={3}
                  />
                </div>

                <div className="form-group">
                  <label>Goal Type</label>
                  <select
                    value={newGoal.goal_type}
                    onChange={(e) => setNewGoal({...newGoal, goal_type: e.target.value})}
                  >
                    <option value="personal">Personal</option>
                    <option value="professional">Professional</option>
                    <option value="health">Health</option>
                    <option value="financial">Financial</option>
                    <option value="learning">Learning</option>
                    <option value="relationship">Relationship</option>
                    <option value="creative">Creative</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={newGoal.priority}
                    onChange={(e) => setNewGoal({...newGoal, priority: e.target.value})}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Target Value</label>
                  <input
                    type="number"
                    value={newGoal.target_value}
                    onChange={(e) => setNewGoal({...newGoal, target_value: e.target.value})}
                    placeholder="e.g., 12"
                  />
                </div>

                <div className="form-group">
                  <label>Unit</label>
                  <input
                    type="text"
                    value={newGoal.unit}
                    onChange={(e) => setNewGoal({...newGoal, unit: e.target.value})}
                    placeholder="e.g., books, pounds, hours"
                  />
                </div>

                <div className="form-group">
                  <label>Target Date</label>
                  <input
                    type="date"
                    value={newGoal.target_date}
                    onChange={(e) => setNewGoal({...newGoal, target_date: e.target.value})}
                  />
                </div>

                <div className="form-group">
                  <label>Time Frame</label>
                  <select
                    value={newGoal.time_frame}
                    onChange={(e) => setNewGoal({...newGoal, time_frame: e.target.value})}
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="create-btn">
                  Create Goal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Goal Details Modal */}
      {selectedGoal && (
        <div className="modal-overlay">
          <div className="modal goal-details-modal">
            <div className="modal-header">
              <h3>{selectedGoal.title}</h3>
              <button 
                className="close-btn"
                onClick={() => setSelectedGoal(null)}
              >
                ×
              </button>
            </div>
            <div className="goal-details">
              <div className="detail-section">
                <h4>Progress</h4>
                <div className="large-progress-bar">
                  <div 
                    className="large-progress-fill"
                    style={{ width: `${selectedGoal.completion_percentage || 0}%` }}
                  />
                </div>
                <span className="large-progress-text">
                  {selectedGoal.completion_percentage?.toFixed(1) || 0}% Complete
                </span>
              </div>

              {selectedGoal.ai_suggestions && (
                <div className="detail-section">
                  <h4>AI Suggestions</h4>
                  <div className="suggestions-list">
                    {selectedGoal.ai_suggestions.map((suggestion, index) => (
                      <div key={index} className="suggestion-item">
                        <h5>{suggestion.title}</h5>
                        <p>{suggestion.description}</p>
                        <span className={`priority-tag ${suggestion.priority}`}>
                          {suggestion.priority} priority
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedGoal.smart_analysis && (
                <div className="detail-section">
                  <h4>SMART Analysis</h4>
                  <div className="smart-breakdown">
                    {Object.entries(selectedGoal.smart_analysis).map(([key, value]) => (
                      key !== 'overall_score' && key !== 'recommendations' && (
                        <div key={key} className="smart-criterion">
                          <span className="criterion-name">
                            {key.charAt(0).toUpperCase() + key.slice(1)}
                          </span>
                          <span className="criterion-score">{value.score}/10</span>
                          <p className="criterion-feedback">{value.feedback}</p>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Goals;