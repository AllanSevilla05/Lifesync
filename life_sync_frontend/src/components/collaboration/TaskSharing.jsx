import React, { useState, useEffect } from 'react';
import { Share2, Users, User, Clock, Send, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './TaskSharing.css';

const TaskSharing = ({ task, onClose, onTaskShared }) => {
  const { user } = useAuth();
  const [teams, setTeams] = useState([]);
  const [shareType, setShareType] = useState('team'); // 'team' or 'user'
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [permission, setPermission] = useState('view');
  const [message, setMessage] = useState('');
  const [expiresHours, setExpiresHours] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const response = await api.get('/collaboration/teams');
      setTeams(response.data.teams || []);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const handleShare = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const shareData = {
        task_id: task.id,
        permission,
        message,
        expires_hours: expiresHours ? parseInt(expiresHours) : null
      };

      if (shareType === 'team' && selectedTeam) {
        shareData.team_id = parseInt(selectedTeam);
      } else if (shareType === 'user' && selectedUser) {
        shareData.user_id = parseInt(selectedUser);
      } else {
        alert('Please select a recipient');
        setLoading(false);
        return;
      }

      const response = await api.post('/collaboration/share-task', shareData);
      
      if (response.data.success) {
        alert('Task shared successfully!');
        if (onTaskShared) onTaskShared();
        onClose();
      }
    } catch (error) {
      console.error('Error sharing task:', error);
      alert(error.response?.data?.detail || 'Failed to share task');
    } finally {
      setLoading(false);
    }
  };

  const permissionOptions = [
    { value: 'view', label: 'View Only', description: 'Can view task details' },
    { value: 'comment', label: 'View & Comment', description: 'Can view and add comments' },
    { value: 'edit', label: 'Edit', description: 'Can view, comment, and edit task' },
    { value: 'admin', label: 'Admin', description: 'Full access to task' }
  ];

  const expirationOptions = [
    { value: '', label: 'Never' },
    { value: '24', label: '24 hours' },
    { value: '72', label: '3 days' },
    { value: '168', label: '1 week' },
    { value: '720', label: '1 month' }
  ];

  return (
    <div className="modal-overlay">
      <div className="task-sharing-modal">
        <div className="modal-header">
          <div className="header-content">
            <Share2 size={20} />
            <h3>Share Task: {task.title}</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleShare} className="sharing-form">
          {/* Share Type Selection */}
          <div className="form-section">
            <label className="section-label">Share With</label>
            <div className="share-type-toggle">
              <button
                type="button"
                className={`toggle-btn ${shareType === 'team' ? 'active' : ''}`}
                onClick={() => setShareType('team')}
              >
                <Users size={16} />
                Team
              </button>
              <button
                type="button"
                className={`toggle-btn ${shareType === 'user' ? 'active' : ''}`}
                onClick={() => setShareType('user')}
              >
                <User size={16} />
                Individual
              </button>
            </div>
          </div>

          {/* Recipient Selection */}
          <div className="form-section">
            {shareType === 'team' ? (
              <div className="form-group">
                <label>Select Team</label>
                <select
                  value={selectedTeam}
                  onChange={(e) => setSelectedTeam(e.target.value)}
                  required
                >
                  <option value="">Choose a team...</option>
                  {teams.map(team => (
                    <option key={team.id} value={team.id}>
                      {team.name} ({team.member_count} members)
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="form-group">
                <label>User Email</label>
                <input
                  type="email"
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  placeholder="Enter user email address"
                  required
                />
                <small>Note: User must be registered on the platform</small>
              </div>
            )}
          </div>

          {/* Permission Level */}
          <div className="form-section">
            <label className="section-label">Permission Level</label>
            <div className="permission-options">
              {permissionOptions.map(option => (
                <label key={option.value} className="permission-option">
                  <input
                    type="radio"
                    name="permission"
                    value={option.value}
                    checked={permission === option.value}
                    onChange={(e) => setPermission(e.target.value)}
                  />
                  <div className="permission-content">
                    <span className="permission-label">{option.label}</span>
                    <span className="permission-description">{option.description}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Message */}
          <div className="form-section">
            <div className="form-group">
              <label>Message (Optional)</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Add a message for the recipients..."
                rows={3}
              />
            </div>
          </div>

          {/* Expiration */}
          <div className="form-section">
            <div className="form-group">
              <label>
                <Clock size={16} />
                Access Expires
              </label>
              <select
                value={expiresHours}
                onChange={(e) => setExpiresHours(e.target.value)}
              >
                {expirationOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              <Send size={16} />
              {loading ? 'Sharing...' : 'Share Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskSharing;