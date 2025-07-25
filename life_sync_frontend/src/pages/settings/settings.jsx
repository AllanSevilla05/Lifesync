import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Bell, Moon, Shield, HelpCircle } from 'lucide-react';
import './settings.css';

const SettingsPage = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate('/main');
  };

  const handleProfileSettingsClick = () => {
    navigate('/profile-settings');
  };

  return (
    <div className="main-container">
      <div className="main-card">
        <div className="settings-header">
          <button 
            onClick={handleBackClick}
            className="back-button"
            aria-label="Go back"
          >
            <ArrowLeft size={24} />
          </button>
          <h1>Settings</h1>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h2>Account</h2>
            <div className="settings-item">
              <User size={20} />
              <span>Profile Settings</span>
              <button onClick={handleProfileSettingsClick}>Edit</button>
            </div>
          </div>

          <div className="settings-section">
            <h2>Preferences</h2>
            <div className="settings-item">
              <Bell size={20} />
              <span>Notifications</span>
              <button onClick={() => alert('Notification settings')}>Configure</button>
            </div>
            <div className="settings-item">
              <Moon size={20} />
              <span>Dark Mode <span style={{ fontStyle: 'italic' }}>(Future Feature)</span></span>
              <label className="toggle-switch">
                <input type="checkbox" />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-section">
            <h2>Support</h2>
            <div className="settings-item">
              <Shield size={20} />
              <span>Privacy Policy</span>
              <button onClick={() => alert('Privacy policy')}>View</button>
            </div>
            <div className="settings-item">
              <HelpCircle size={20} />
              <span>Help & Support</span>
              <button onClick={() => alert('Help & support')}>Contact</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;