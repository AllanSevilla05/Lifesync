import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Heart, TrendingUp, BarChart3, Calendar } from 'lucide-react';
import './mood_calendar.css'; // Assuming you have a CSS file for styling

const MoodCalendarPage = () => {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const moods = [
    { id: 1, emoji: '😊', label: 'Great', color: '#10b981' },
    { id: 2, emoji: '🙂', label: 'Good', color: '#3b82f6' },
    { id: 3, emoji: '😐', label: 'Okay', color: '#f59e0b' },
    { id: 4, emoji: '😔', label: 'Low', color: '#ef4444' },
    { id: 5, emoji: '😢', label: 'Sad', color: '#8b5cf6' }
  ];

  // Sample mood data - replace with actual data
  const moodData = {
    '2025-07-25': moods[0], // Great
    '2025-07-24': moods[1], // Good
    '2025-07-23': moods[2], // Okay
    '2025-07-22': moods[0], // Great
    '2025-07-21': moods[3], // Low
    '2025-07-20': moods[1], // Good
    '2025-07-19': moods[4], // Sad
    '2025-07-18': moods[0], // Great
    '2025-07-17': moods[2], // Okay
    '2025-07-16': moods[1], // Good
  };

  const handleBackClick = () => {
    navigate('/main');
  };

  const formatDateKey = (date) => {
    return date.toISOString().split('T')[0];
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }

    return days;
  };

  const navigateMonth = (direction) => {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(newMonth.getMonth() + direction);
    setCurrentMonth(newMonth);
  };

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const getMoodStats = () => {
    const moodCounts = moods.reduce((acc, mood) => {
      acc[mood.id] = 0;
      return acc;
    }, {});

    Object.values(moodData).forEach(mood => {
      if (mood) moodCounts[mood.id]++;
    });

    const total = Object.values(moodCounts).reduce((sum, count) => sum + count, 0);
    
    return moods.map(mood => ({
      ...mood,
      count: moodCounts[mood.id],
      percentage: total > 0 ? Math.round((moodCounts[mood.id] / total) * 100) : 0
    }));
  };

  const handleDateClick = (date, mood) => {
    if (!date) return;
    setSelectedDate(date);
    // Here you could open a modal to edit the mood for this date
    console.log('Selected date:', date, 'Current mood:', mood);
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const moodStats = getMoodStats();
  const days = getDaysInMonth(currentMonth);

  return (
    <div className="mood-calendar-container">
      <div className="mood-calendar-card">
        {/* Header */}
        <div className="mood-calendar-header">
          <button 
            onClick={handleBackClick}
            className="back-button"
            aria-label="Go back to main page"
          >
            <ArrowLeft size={24} />
          </button>
          <h1>
            <Heart size={24} />
            Mood Calendar
          </h1>
        </div>

        <div className="mood-calendar-content">
          {/* Calendar Section */}
          <div className="calendar-section">
            <div className="calendar-header">
              <button 
                onClick={() => navigateMonth(-1)}
                className="nav-button"
                aria-label="Previous month"
              >
                ‹
              </button>
              <h2>
                {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
              </h2>
              <button 
                onClick={() => navigateMonth(1)}
                className="nav-button"
                aria-label="Next month"
              >
                ›
              </button>
            </div>

            <div className="calendar-grid">
              {/* Weekday headers */}
              {weekdays.map(day => (
                <div key={day} className="weekday-header">
                  {day}
                </div>
              ))}

              {/* Calendar days */}
              {days.map((date, index) => {
                if (!date) {
                  return <div key={index} className="empty-day"></div>;
                }

                const dateKey = formatDateKey(date);
                const dayMood = moodData[dateKey];
                const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();

                return (
                  <div 
                    key={index}
                    className={`calendar-day ${isToday(date) ? 'today' : ''} ${isSelected ? 'selected' : ''} ${dayMood ? 'has-mood' : ''}`}
                    onClick={() => handleDateClick(date, dayMood)}
                  >
                    <span className="day-number">{date.getDate()}</span>
                    {dayMood && (
                      <div 
                        className="mood-indicator"
                        style={{ backgroundColor: dayMood.color }}
                      >
                        <span className="mood-emoji-small">{dayMood.emoji}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Stats Section */}
          <div className="stats-section">
            <div className="stats-header">
              <TrendingUp size={20} />
              <h3>Mood Statistics</h3>
            </div>

            <div className="mood-stats">
              {moodStats.map(mood => (
                <div key={mood.id} className="mood-stat-item">
                  <div className="mood-stat-info">
                    <span className="stat-emoji">{mood.emoji}</span>
                    <span className="stat-label">{mood.label}</span>
                  </div>
                  <div className="mood-stat-bar">
                    <div 
                      className="stat-fill"
                      style={{ 
                        width: `${mood.percentage}%`,
                        backgroundColor: mood.color 
                      }}
                    ></div>
                  </div>
                  <span className="stat-percentage">{mood.percentage}%</span>
                </div>
              ))}
            </div>

            <div className="mood-summary">
              <BarChart3 size={16} />
              <span>Tracked {Object.keys(moodData).length} days this month</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MoodCalendarPage;