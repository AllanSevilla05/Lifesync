import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Check, Clock, Brain, Heart, Target } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import ApiService from '../../services/api';
import './Onboarding.css';

const Onboarding = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    productivity_peak: 'morning',
    work_schedule: 'flexible',
    goals: [],
    notification_preferences: {
      task_reminders: true,
      daily_summary: true,
      break_reminders: true,
      wellness_check: true
    },
    wellness_focus: [],
    experience_level: 'beginner'
  });

  const steps = [
    {
      id: 'welcome',
      title: 'Welcome to LifeSync!',
      subtitle: 'Let\'s personalize your productivity journey',
      icon: <Target size={32} />
    },
    {
      id: 'productivity',
      title: 'When are you most productive?',
      subtitle: 'This helps us schedule your tasks optimally',
      icon: <Brain size={32} />
    },
    {
      id: 'goals',
      title: 'What are your main goals?',
      subtitle: 'Select all that apply to you',
      icon: <Target size={32} />
    },
    {
      id: 'wellness',
      title: 'Wellness & Self-Care',
      subtitle: 'What wellness areas would you like to focus on?',
      icon: <Heart size={32} />
    },
    {
      id: 'notifications',
      title: 'Notification Preferences',
      subtitle: 'Choose how you\'d like to stay informed',
      icon: <Clock size={32} />
    },
    {
      id: 'complete',
      title: 'You\'re all set!',
      subtitle: 'Let\'s start your productivity journey',
      icon: <Check size={32} />
    }
  ];

  const productivityOptions = [
    { value: 'morning', label: 'Morning (6 AM - 12 PM)', description: 'I\'m most alert and focused in the morning' },
    { value: 'afternoon', label: 'Afternoon (12 PM - 6 PM)', description: 'I hit my stride in the afternoon' },
    { value: 'evening', label: 'Evening (6 PM - 12 AM)', description: 'I\'m a night owl and work best in the evening' },
    { value: 'flexible', label: 'It varies', description: 'My productive time changes day to day' }
  ];

  const goalOptions = [
    { id: 'academic', label: 'Academic Success', icon: '🎓' },
    { id: 'career', label: 'Career Growth', icon: '💼' },
    { id: 'fitness', label: 'Health & Fitness', icon: '💪' },
    { id: 'creative', label: 'Creative Projects', icon: '🎨' },
    { id: 'personal', label: 'Personal Development', icon: '🌱' },
    { id: 'social', label: 'Social & Relationships', icon: '👥' },
    { id: 'financial', label: 'Financial Goals', icon: '💰' },
    { id: 'hobbies', label: 'Hobbies & Interests', icon: '🎯' }
  ];

  const wellnessOptions = [
    { id: 'stress', label: 'Stress Management', icon: '🧘‍♀️' },
    { id: 'sleep', label: 'Better Sleep', icon: '😴' },
    { id: 'exercise', label: 'Regular Exercise', icon: '🏃‍♂️' },
    { id: 'mindfulness', label: 'Mindfulness & Meditation', icon: '🧠' },
    { id: 'nutrition', label: 'Healthy Eating', icon: '🥗' },
    { id: 'social', label: 'Social Connection', icon: '🤝' },
    { id: 'work_life', label: 'Work-Life Balance', icon: '⚖️' },
    { id: 'mental_health', label: 'Mental Health', icon: '💚' }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleGoalToggle = (goalId) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.includes(goalId)
        ? prev.goals.filter(id => id !== goalId)
        : [...prev.goals, goalId]
    }));
  };

  const handleWellnessToggle = (wellnessId) => {
    setFormData(prev => ({
      ...prev,
      wellness_focus: prev.wellness_focus.includes(wellnessId)
        ? prev.wellness_focus.filter(id => id !== wellnessId)
        : [...prev.wellness_focus, wellnessId]
    }));
  };

  const handleNotificationToggle = (type) => {
    setFormData(prev => ({
      ...prev,
      notification_preferences: {
        ...prev.notification_preferences,
        [type]: !prev.notification_preferences[type]
      }
    }));
  };

  const handleComplete = async () => {
    try {
      // Save preferences to backend
      await ApiService.request('/auth/preferences', {
        method: 'POST',
        body: formData
      });

      // Mark onboarding as completed
      await ApiService.request('/auth/onboarding-complete', {
        method: 'POST'
      });

      navigate('/main');
    } catch (error) {
      console.error('Failed to save onboarding preferences:', error);
      // Still navigate to main app even if preferences fail to save
      navigate('/main');
    }
  };

  const renderStepContent = () => {
    const step = steps[currentStep];

    switch (step.id) {
      case 'welcome':
        return (
          <div className="step-content welcome-step">
            <div className="welcome-animation">
              <div className="welcome-logo">
                <img src="/images/LifeSyncLogo.png" alt="LifeSync" />
              </div>
              <div className="welcome-text">
                <p>LifeSync is your AI-powered productivity and wellness assistant.</p>
                <p>Let's take a few minutes to personalize your experience!</p>
              </div>
            </div>
          </div>
        );

      case 'productivity':
        return (
          <div className="step-content">
            <div className="options-grid">
              {productivityOptions.map(option => (
                <div
                  key={option.value}
                  className={`option-card ${formData.productivity_peak === option.value ? 'selected' : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, productivity_peak: option.value }))}
                >
                  <div className="option-header">
                    <h4>{option.label}</h4>
                  </div>
                  <p>{option.description}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case 'goals':
        return (
          <div className="step-content">
            <div className="multi-select-grid">
              {goalOptions.map(goal => (
                <div
                  key={goal.id}
                  className={`select-card ${formData.goals.includes(goal.id) ? 'selected' : ''}`}
                  onClick={() => handleGoalToggle(goal.id)}
                >
                  <div className="card-icon">{goal.icon}</div>
                  <div className="card-label">{goal.label}</div>
                  {formData.goals.includes(goal.id) && (
                    <div className="selected-indicator">
                      <Check size={16} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      case 'wellness':
        return (
          <div className="step-content">
            <div className="multi-select-grid">
              {wellnessOptions.map(wellness => (
                <div
                  key={wellness.id}
                  className={`select-card ${formData.wellness_focus.includes(wellness.id) ? 'selected' : ''}`}
                  onClick={() => handleWellnessToggle(wellness.id)}
                >
                  <div className="card-icon">{wellness.icon}</div>
                  <div className="card-label">{wellness.label}</div>
                  {formData.wellness_focus.includes(wellness.id) && (
                    <div className="selected-indicator">
                      <Check size={16} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="step-content">
            <div className="notification-options">
              {Object.entries(formData.notification_preferences).map(([key, value]) => (
                <div key={key} className="notification-item">
                  <div className="notification-info">
                    <h4>{key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                    <p>
                      {key === 'task_reminders' && 'Get notified when tasks are due'}
                      {key === 'daily_summary' && 'Receive a daily progress summary'}
                      {key === 'break_reminders' && 'Gentle reminders to take breaks'}
                      {key === 'wellness_check' && 'Periodic wellness and mood check-ins'}
                    </p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() => handleNotificationToggle(key)}
                    />
                    <span className="slider"></span>
                  </label>
                </div>
              ))}
            </div>
          </div>
        );

      case 'complete':
        return (
          <div className="step-content complete-step">
            <div className="completion-animation">
              <div className="success-icon">
                <Check size={48} />
              </div>
              <div className="completion-text">
                <p>Perfect! Your LifeSync experience is now personalized just for you.</p>
                <div className="summary-cards">
                  <div className="summary-card">
                    <strong>Productivity Peak:</strong> {formData.productivity_peak}
                  </div>
                  <div className="summary-card">
                    <strong>Goals Selected:</strong> {formData.goals.length}
                  </div>
                  <div className="summary-card">
                    <strong>Wellness Focus:</strong> {formData.wellness_focus.length} areas
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        {/* Progress Bar */}
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* Step Counter */}
        <div className="step-counter">
          Step {currentStep + 1} of {steps.length}
        </div>

        {/* Step Content */}
        <div className="step-header">
          <div className="step-icon">
            {steps[currentStep].icon}
          </div>
          <h1>{steps[currentStep].title}</h1>
          <p>{steps[currentStep].subtitle}</p>
        </div>

        {renderStepContent()}

        {/* Navigation */}
        <div className="navigation-buttons">
          <button
            className="nav-button secondary"
            onClick={handlePrevious}
            disabled={currentStep === 0}
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {currentStep === steps.length - 1 ? (
            <button
              className="nav-button primary"
              onClick={handleComplete}
            >
              Get Started
              <ChevronRight size={20} />
            </button>
          ) : (
            <button
              className="nav-button primary"
              onClick={handleNext}
            >
              Next
              <ChevronRight size={20} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;