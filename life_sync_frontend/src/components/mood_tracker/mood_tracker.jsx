import React, { useState } from 'react';
import { Heart, TrendingUp, Calendar, ChevronRight } from 'lucide-react';
import './mood_tracker.css'; // Assuming you have a CSS file for styling

const MoodTracker = ({ onViewMoodCalendar }) => {
  const [selectedMood, setSelectedMood] = useState(null);
  const [todayMood, setTodayMood] = useState(null);

  const moods = [
    { id: 1, emoji: '😊', label: 'Great', color: '#10b981' },
    { id: 2, emoji: '🙂', label: 'Good', color: '#3b82f6' },
    { id: 3, emoji: '😐', label: 'Okay', color: '#f59e0b' },
    { id: 4, emoji: '😔', label: 'Low', color: '#ef4444' },
    { id: 5, emoji: '😢', label: 'Sad', color: '#8b5cf6' }
  ];

  // Sample mood data for the week
  const weekMoods = [
    { day: 'Mon', mood: moods[0] },
    { day: 'Tue', mood: moods[1] },
    { day: 'Wed', mood: moods[2] },
    { day: 'Thu', mood: null },
    { day: 'Fri', mood: null },
    { day: 'Sat', mood: null },
    { day: 'Sun', mood: null }
  ];

  const handleMoodSelect = (mood) => {
    setSelectedMood(mood);
    setTodayMood(mood);
    // Here you would typically save the mood to your data store
    console.log('Mood saved:', mood);
  };

  const getTodayName = () => {
    const today = new Date();
    return today.toLocaleDateString('en-US', { weekday: 'short' });
  };

  return (
    <div className="mood-tracker">
      <div className="mood-tracker-header">
        <div className="mood-tracker-title">
          <Heart size={20} />
          <h3>How are you feeling today?</h3>
        </div>
      </div>

      <div className="mood-tracker-content">
        {/* Today's Mood Selection */}
        <div className="today-mood-section">
          <div className="mood-options">
            {moods.map((mood) => (
              <button
                key={mood.id}
                className={`mood-button ${selectedMood?.id === mood.id ? 'selected' : ''} ${todayMood?.id === mood.id ? 'saved' : ''}`}
                onClick={() => handleMoodSelect(mood)}
                style={{ '--mood-color': mood.color }}
                aria-label={`Select ${mood.label} mood`}
              >
                <span className="mood-emoji">{mood.emoji}</span>
                <span className="mood-label">{mood.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Week Overview */}
        <div className="week-overview">
          <div className="week-header">
            <TrendingUp size={16} />
            <span>This Week</span>
          </div>
          <div className="week-moods">
            {weekMoods.map((dayMood, index) => {
              const isToday = dayMood.day === getTodayName();
              const displayMood = isToday ? (todayMood || dayMood.mood) : dayMood.mood;
              
              return (
                <div 
                  key={index} 
                  className={`day-mood ${isToday ? 'today' : ''} ${displayMood ? 'has-mood' : ''}`}
                >
                  <span className="day-label">{dayMood.day}</span>
                  <div className="day-mood-indicator">
                    {displayMood ? (
                      <span 
                        className="day-emoji"
                        style={{ color: displayMood.color }}
                      >
                        {displayMood.emoji}
                      </span>
                    ) : (
                      <div className="empty-mood"></div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* View Mood Calendar Button */}
        <button 
          className="view-mood-calendar-btn"
          onClick={onViewMoodCalendar}
          aria-label="View mood calendar"
        >
          <Calendar size={18} />
          View Mood Calendar
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
};

export default MoodTracker;