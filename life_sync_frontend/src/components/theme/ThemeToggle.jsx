import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import './ThemeToggle.css';

const ThemeToggle = ({ showLabels = false, variant = 'button' }) => {
  const { theme, toggleTheme, setLightTheme, setDarkTheme, setSystemTheme, isDark } = useTheme();

  if (variant === 'dropdown') {
    return (
      <div className="theme-dropdown">
        <div className="theme-options">
          <button
            onClick={setLightTheme}
            className={`theme-option ${theme === 'light' ? 'active' : ''}`}
            aria-label="Light theme"
          >
            <Sun size={16} />
            {showLabels && <span>Light</span>}
          </button>
          <button
            onClick={setDarkTheme}
            className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
            aria-label="Dark theme"
          >
            <Moon size={16} />
            {showLabels && <span>Dark</span>}
          </button>
          <button
            onClick={setSystemTheme}
            className="theme-option"
            aria-label="System theme"
          >
            <Monitor size={16} />
            {showLabels && <span>System</span>}
          </button>
        </div>
      </div>
    );
  }

  if (variant === 'switch') {
    return (
      <div className="theme-switch">
        <Sun size={16} className={`theme-icon ${!isDark ? 'active' : ''}`} />
        <label className="switch-container">
          <input
            type="checkbox"
            checked={isDark}
            onChange={toggleTheme}
            aria-label="Toggle dark mode"
          />
          <span className="switch-slider">
            <span className="switch-thumb" />
          </span>
        </label>
        <Moon size={16} className={`theme-icon ${isDark ? 'active' : ''}`} />
      </div>
    );
  }

  // Default button variant
  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle-button"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <div className={`theme-toggle-icon ${isDark ? 'spinning' : ''}`}>
        {isDark ? <Sun size={20} /> : <Moon size={20} />}
      </div>
      {showLabels && (
        <span className="theme-toggle-label">
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </span>
      )}
    </button>
  );
};

export default ThemeToggle;