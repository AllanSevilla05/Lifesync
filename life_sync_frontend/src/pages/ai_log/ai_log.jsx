import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Bot, 
  User, 
  Clock, 
  TrendingUp, 
  CheckCircle, 
  XCircle, 
  MoreHorizontal,
  Search,
  Filter,
  Calendar
} from 'lucide-react';
import './ai_log.css'; // Assuming you have a CSS file for styling

const AIInteractionLog = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, accepted, dismissed
  const [selectedInteraction, setSelectedInteraction] = useState(null);

  // Sample AI interaction data - replace with actual data
  const interactions = [
    {
      id: 1,
      suggestion: "You are most productive in the morning. Would you like to change your gym session for tomorrow morning?",
      userResponse: "accepted",
      responseDetails: "Moved gym session from 7:00 PM to 6:00 AM",
      timestamp: new Date('2025-07-25T14:30:00'),
      type: "schedule_optimization",
      context: "Based on productivity patterns",
      outcome: "Event rescheduled successfully"
    },
    {
      id: 2,
      suggestion: "You have a doctor appointment tomorrow at 9 AM. Would you like me to set a reminder to prepare your medical documents?",
      userResponse: "accepted",
      responseDetails: "Set reminder for 8:00 AM to gather documents",
      timestamp: new Date('2025-07-24T16:45:00'),
      type: "preparation_reminder",
      context: "Upcoming appointment",
      outcome: "Reminder created"
    },
    {
      id: 3,
      suggestion: "I noticed you've been feeling low this week. Would you like me to suggest some mood-boosting activities?",
      userResponse: "dismissed",
      responseDetails: "User chose to handle mood independently",
      timestamp: new Date('2025-07-23T11:20:00'),
      type: "wellness_suggestion",
      context: "Mood tracking analysis",
      outcome: "No action taken"
    },
    {
      id: 4,
      suggestion: "Your yoga class conflicts with your lunch meeting on Friday. Should I help you reschedule one of them?",
      userResponse: "accepted",
      responseDetails: "Rescheduled yoga class to Saturday morning",
      timestamp: new Date('2025-07-22T09:15:00'),
      type: "conflict_resolution",
      context: "Schedule conflict detected",
      outcome: "Conflict resolved"
    },
    {
      id: 5,
      suggestion: "Based on your recent activities, would you like me to block out focus time for your work projects?",
      userResponse: "dismissed",
      responseDetails: "User prefers manual scheduling",
      timestamp: new Date('2025-07-21T13:10:00'),
      type: "productivity_optimization",
      context: "Activity pattern analysis",
      outcome: "No changes made"
    },
    {
      id: 6,
      suggestion: "You haven't had a break today. Would you like me to schedule a 15-minute break now?",
      userResponse: "accepted",
      responseDetails: "Scheduled 15-minute break",
      timestamp: new Date('2025-07-20T15:30:00'),
      type: "wellness_suggestion",
      context: "Break pattern monitoring",
      outcome: "Break scheduled"
    }
  ];

  const handleBackClick = () => {
    navigate('/main');
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diffHours = Math.abs(now - timestamp) / (1000 * 60 * 60);
    
    if (diffHours < 24) {
      return timestamp.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    } else if (diffHours < 48) {
      return 'Yesterday';
    } else {
      return timestamp.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric'
      });
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'schedule_optimization':
        return <Calendar size={16} />;
      case 'preparation_reminder':
        return <Clock size={16} />;
      case 'wellness_suggestion':
        return <TrendingUp size={16} />;
      case 'conflict_resolution':
        return <MoreHorizontal size={16} />;
      case 'productivity_optimization':
        return <TrendingUp size={16} />;
      default:
        return <Bot size={16} />;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'schedule_optimization':
        return 'Schedule Optimization';
      case 'preparation_reminder':
        return 'Preparation Reminder';
      case 'wellness_suggestion':
        return 'Wellness Suggestion';
      case 'conflict_resolution':
        return 'Conflict Resolution';
      case 'productivity_optimization':
        return 'Productivity Optimization';
      default:
        return 'AI Suggestion';
    }
  };

  const filteredInteractions = interactions
    .filter(interaction => {
      const matchesSearch = interaction.suggestion.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           interaction.context.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filterStatus === 'all' || interaction.userResponse === filterStatus;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => b.timestamp - a.timestamp);

  const getStats = () => {
    const total = interactions.length;
    const accepted = interactions.filter(i => i.userResponse === 'accepted').length;
    const dismissed = interactions.filter(i => i.userResponse === 'dismissed').length;
    const acceptanceRate = total > 0 ? Math.round((accepted / total) * 100) : 0;

    return { total, accepted, dismissed, acceptanceRate };
  };

  const stats = getStats();

  return (
    <div className="ai-log-container">
      <div className="ai-log-card">
        {/* Header */}
        <div className="ai-log-header">
          <button 
            onClick={handleBackClick}
            className="back-button"
            aria-label="Go back to main page"
          >
            <ArrowLeft size={24} />
          </button>
          <h1>
            <Bot size={24} />
            AI Interaction Log
          </h1>
        </div>

        {/* Stats Overview */}
        <div className="stats-overview">
          <div className="stat-card">
            <div className="stat-number">{stats.total}</div>
            <div className="stat-label">Total Suggestions</div>
          </div>
          <div className="stat-card accepted">
            <div className="stat-number">{stats.accepted}</div>
            <div className="stat-label">Accepted</div>
          </div>
          <div className="stat-card dismissed">
            <div className="stat-number">{stats.dismissed}</div>
            <div className="stat-label">Dismissed</div>
          </div>
          <div className="stat-card rate">
            <div className="stat-number">{stats.acceptanceRate}%</div>
            <div className="stat-label">Acceptance Rate</div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="controls-section">
          <div className="search-bar">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search interactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="filter-section">
            <Filter size={18} />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Interactions</option>
              <option value="accepted">Accepted Only</option>
              <option value="dismissed">Dismissed Only</option>
            </select>
          </div>
        </div>

        {/* Interactions List */}
        <div className="interactions-list">
          <h2>Recent Interactions</h2>
          {filteredInteractions.length === 0 ? (
            <div className="no-interactions">
              <Bot size={48} />
              <p>No interactions found</p>
              <span>Try adjusting your search or filter criteria</span>
            </div>
          ) : (
            <div className="interactions-grid">
              {filteredInteractions.map((interaction) => (
                <div 
                  key={interaction.id} 
                  className={`interaction-card ${interaction.userResponse}`}
                  onClick={() => setSelectedInteraction(interaction)}
                >
                  <div className="interaction-header">
                    <div className="interaction-type">
                      {getTypeIcon(interaction.type)}
                      <span>{getTypeLabel(interaction.type)}</span>
                    </div>
                    <div className="interaction-timestamp">
                      {formatTimestamp(interaction.timestamp)}
                    </div>
                  </div>

                  <div className="interaction-content">
                    <div className="ai-suggestion">
                      <Bot size={16} />
                      <p>{interaction.suggestion}</p>
                    </div>
                    
                    <div className={`user-response ${interaction.userResponse}`}>
                      {interaction.userResponse === 'accepted' ? (
                        <CheckCircle size={16} />
                      ) : (
                        <XCircle size={16} />
                      )}
                      <span>
                        {interaction.userResponse === 'accepted' ? 'Accepted' : 'Dismissed'}
                      </span>
                    </div>
                  </div>

                  <div className="interaction-context">
                    <span>Context: {interaction.context}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Interaction Detail Modal */}
        {selectedInteraction && (
          <div className="interaction-modal-overlay" onClick={() => setSelectedInteraction(null)}>
            <div className="interaction-modal" onClick={(e) => e.stopPropagation()}>
              <div className="interaction-modal-header">
                <h3>{getTypeLabel(selectedInteraction.type)}</h3>
                <button onClick={() => setSelectedInteraction(null)} className="close-button">
                  ×
                </button>
              </div>
              
              <div className="interaction-modal-content">
                <div className="modal-section">
                  <h4>AI Suggestion</h4>
                  <p>{selectedInteraction.suggestion}</p>
                </div>

                <div className="modal-section">
                  <h4>Your Response</h4>
                  <div className={`response-badge ${selectedInteraction.userResponse}`}>
                    {selectedInteraction.userResponse === 'accepted' ? (
                      <CheckCircle size={16} />
                    ) : (
                      <XCircle size={16} />
                    )}
                    <span>{selectedInteraction.userResponse === 'accepted' ? 'Accepted' : 'Dismissed'}</span>
                  </div>
                  <p>{selectedInteraction.responseDetails}</p>
                </div>

                <div className="modal-section">
                  <h4>Context & Outcome</h4>
                  <p><strong>Context:</strong> {selectedInteraction.context}</p>
                  <p><strong>Outcome:</strong> {selectedInteraction.outcome}</p>
                  <p><strong>Time:</strong> {selectedInteraction.timestamp.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIInteractionLog;