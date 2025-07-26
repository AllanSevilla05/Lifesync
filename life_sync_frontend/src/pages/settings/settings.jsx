import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Bell, Moon, Shield, HelpCircle, Download, Users } from 'lucide-react';
import DataExport from './data-export/DataExport';
import ThemeToggle from '../../components/theme/ThemeToggle';
import './settings.css';

const SettingsPage = () => {
  const navigate = useNavigate();
  const [showDataExport, setShowDataExport] = useState(false);

  const handleBackClick = () => {
    navigate('/main');
  };

  const handleProfileSettingsClick = () => {
    navigate('/profile-settings');
  };

  if (showDataExport) {
    return (
      <div className="main-container">
        <div className="main-card">
          <div className="settings-header">
            <button 
              onClick={() => setShowDataExport(false)}
              className="back-button"
              aria-label="Go back to settings"
            >
              <ArrowLeft size={24} />
            </button>
            <h1>Export Data</h1>
          </div>
          <DataExport />
        </div>
      </div>
    );
  }

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
              <div className="setting-content">
                <span>Theme</span>
                <p className="setting-description">Choose between light, dark, or system theme</p>
              </div>
              <ThemeToggle variant="dropdown" showLabels={true} />
            </div>
          </div>

          <div className="settings-section">
            <h2>Collaboration</h2>
            <div className="settings-item">
              <Users size={20} />
              <span>Teams & Sharing</span>
              <button onClick={() => navigate('/teams')}>Manage</button>
            </div>
          </div>

          <div className="settings-section">
            <h2>Data & Privacy</h2>
            <div className="settings-item">
              <Download size={20} />
              <span>Export Data</span>
              <button onClick={() => setShowDataExport(true)}>Export</button>
            </div>
            <div className="settings-item">
              <Shield size={20} />
              <span>Privacy Policy</span>
              <button onClick={() => alert('Privacy policy')}>View</button>
            </div>
          </div>

          <div className="settings-section">
            <h2>Support</h2>
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