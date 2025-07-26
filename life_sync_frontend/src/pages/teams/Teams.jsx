import React, { useState, useEffect } from 'react';
import { Users, Plus, Copy, UserPlus, Settings, Calendar, MessageSquare } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Teams.css';

const Teams = () => {
  const { user } = useAuth();
  const [teams, setTeams] = useState([]);
  const [sharedTasks, setSharedTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateTeam, setShowCreateTeam] = useState(false);
  const [showJoinTeam, setShowJoinTeam] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', description: '' });
  const [joinCode, setJoinCode] = useState('');
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteData, setInviteData] = useState({ email: '', permission: 'view', message: '' });

  useEffect(() => {
    fetchTeamsAndTasks();
  }, []);

  const fetchTeamsAndTasks = async () => {
    try {
      const [teamsResponse, tasksResponse] = await Promise.all([
        api.get('/collaboration/teams'),
        api.get('/collaboration/shared-tasks')
      ]);
      
      setTeams(teamsResponse.data.teams || []);
      setSharedTasks(tasksResponse.data.shared_tasks || []);
    } catch (error) {
      console.error('Error fetching collaboration data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/collaboration/teams', newTeam);
      if (response.data.success) {
        setTeams([...teams, response.data.team]);
        setNewTeam({ name: '', description: '' });
        setShowCreateTeam(false);
      }
    } catch (error) {
      console.error('Error creating team:', error);
      alert('Failed to create team');
    }
  };

  const handleJoinTeam = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/collaboration/teams/join', { team_code: joinCode });
      if (response.data.success) {
        await fetchTeamsAndTasks(); // Refresh data
        setJoinCode('');
        setShowJoinTeam(false);
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error joining team:', error);
      alert(error.response?.data?.detail || 'Failed to join team');
    }
  };

  const handleInviteUser = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post(`/collaboration/teams/${selectedTeam.id}/invite`, inviteData);
      if (response.data.success) {
        setInviteData({ email: '', permission: 'view', message: '' });
        setShowInviteModal(false);
        alert('Invitation sent successfully!');
      }
    } catch (error) {
      console.error('Error sending invitation:', error);
      alert(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const copyTeamCode = (teamCode) => {
    navigator.clipboard.writeText(teamCode);
    alert('Team code copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="teams-container">
        <div className="loading">Loading collaboration data...</div>
      </div>
    );
  }

  return (
    <div className="teams-container">
      <div className="teams-header">
        <div className="header-content">
          <Users size={24} />
          <h1>Teams & Collaboration</h1>
        </div>
        <div className="header-actions">
          <button 
            className="btn-secondary"
            onClick={() => setShowJoinTeam(true)}
          >
            Join Team
          </button>
          <button 
            className="btn-primary"
            onClick={() => setShowCreateTeam(true)}
          >
            <Plus size={16} />
            Create Team
          </button>
        </div>
      </div>

      <div className="teams-content">
        {/* Teams Section */}
        <div className="teams-section">
          <h2>My Teams</h2>
          {teams.length === 0 ? (
            <div className="empty-state">
              <Users size={48} />
              <p>You're not part of any teams yet</p>
              <button 
                className="btn-primary"
                onClick={() => setShowCreateTeam(true)}
              >
                Create Your First Team
              </button>
            </div>
          ) : (
            <div className="teams-grid">
              {teams.map(team => (
                <div key={team.id} className="team-card">
                  <div className="team-header">
                    <h3>{team.name}</h3>
                    {team.is_owner && <div className="owner-badge">Owner</div>}
                  </div>
                  <p className="team-description">{team.description}</p>
                  <div className="team-stats">
                    <span>{team.member_count} members</span>
                    <span className="role-badge">{team.user_role}</span>
                  </div>
                  <div className="team-actions">
                    <button 
                      className="btn-icon"
                      onClick={() => copyTeamCode(team.team_code)}
                      title="Copy team code"
                    >
                      <Copy size={16} />
                    </button>
                    <button 
                      className="btn-icon"
                      onClick={() => {
                        setSelectedTeam(team);
                        setShowInviteModal(true);
                      }}
                      title="Invite member"
                    >
                      <UserPlus size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Shared Tasks Section */}
        <div className="shared-tasks-section">
          <h2>Shared Tasks</h2>
          {sharedTasks.length === 0 ? (
            <div className="empty-state">
              <MessageSquare size={48} />
              <p>No shared tasks yet</p>
            </div>
          ) : (
            <div className="shared-tasks-list">
              {sharedTasks.map(sharedTask => (
                <div key={sharedTask.shared_task_id} className="shared-task-card">
                  <div className="task-content">
                    <h4>{sharedTask.task.title}</h4>
                    <p>{sharedTask.task.description}</p>
                    <div className="task-meta">
                      <span className="shared-by">
                        Shared by {sharedTask.shared_by.full_name}
                      </span>
                      <span className="permission-badge">
                        {sharedTask.permission}
                      </span>
                    </div>
                  </div>
                  <div className="task-actions">
                    {sharedTask.comment_count > 0 && (
                      <div className="comment-count">
                        <MessageSquare size={14} />
                        {sharedTask.comment_count}
                      </div>
                    )}
                    <span className="task-status">{sharedTask.task.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Team Modal */}
      {showCreateTeam && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Team</h3>
              <button 
                className="close-btn"
                onClick={() => setShowCreateTeam(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleCreateTeam}>
              <div className="form-group">
                <label>Team Name</label>
                <input
                  type="text"
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({...newTeam, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newTeam.description}
                  onChange={(e) => setNewTeam({...newTeam, description: e.target.value})}
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateTeam(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create Team
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Team Modal */}
      {showJoinTeam && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Join Team</h3>
              <button 
                className="close-btn"
                onClick={() => setShowJoinTeam(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleJoinTeam}>
              <div className="form-group">
                <label>Team Code</label>
                <input
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="Enter team code"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowJoinTeam(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Join Team
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Invite User Modal */}
      {showInviteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Invite to {selectedTeam?.name}</h3>
              <button 
                className="close-btn"
                onClick={() => setShowInviteModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleInviteUser}>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={inviteData.email}
                  onChange={(e) => setInviteData({...inviteData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Permission Level</label>
                <select
                  value={inviteData.permission}
                  onChange={(e) => setInviteData({...inviteData, permission: e.target.value})}
                >
                  <option value="view">View Only</option>
                  <option value="comment">View & Comment</option>
                  <option value="edit">Edit</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Message (Optional)</label>
                <textarea
                  value={inviteData.message}
                  onChange={(e) => setInviteData({...inviteData, message: e.target.value})}
                  rows={3}
                  placeholder="Add a personal message..."
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowInviteModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Teams;