import React from 'react';
import { Calendar, Clock, ChevronRight } from 'lucide-react';
import './mini_agenda.css'; // Import your custom styles

const MiniAgenda = ({ notificationsData, onViewCalendar }) => {
  // Get upcoming events from notifications data
  const getUpcomingEvents = () => {
    const now = new Date();
    const allNotifications = [
      ...notificationsData.pastDue,
      ...notificationsData.comingUp
    ];

    // Filter for future events and sort by date
    return allNotifications
      .filter(notification => new Date(notification.datetime) > now)
      .sort((a, b) => new Date(a.datetime) - new Date(b.datetime))
      .slice(0, 4); // Show only next 4 events
  };

  const formatEventDate = (datetime) => {
    const date = new Date(datetime);
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const isToday = date.toDateString() === now.toDateString();
    const isTomorrow = date.toDateString() === tomorrow.toDateString();
    
    if (isToday) {
      return `Today, ${date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })}`;
    } else if (isTomorrow) {
      return `Tomorrow, ${date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })}`;
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    }
  };

  const getTimeUntilEvent = (datetime) => {
    const now = new Date();
    const eventDate = new Date(datetime);
    const diffMs = eventDate - now;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `in ${diffDays} day${diffDays > 1 ? 's' : ''}`;
    } else if (diffHours > 0) {
      return `in ${diffHours} hour${diffHours > 1 ? 's' : ''}`;
    } else {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `in ${diffMinutes} min${diffMinutes > 1 ? 's' : ''}`;
    }
  };

  const upcomingEvents = getUpcomingEvents();

  return (
    <div className="mini-agenda">
      <div className="mini-agenda-header">
        <div className="mini-agenda-title">
          <Calendar size={20} />
          <h3>Upcoming Events</h3>
        </div>
        <button 
          className="view-cal-btn"
          onClick={onViewCalendar}
          aria-label="View full calendar"
        >
          View Calendar
          <ChevronRight size={16} />
        </button>
      </div>

      <div className="mini-agenda-content">
        {upcomingEvents.length === 0 ? (
          <div className="no-events">
            <Clock size={24} />
            <p>No upcoming events</p>
            <span>You're all caught up!</span>
          </div>
        ) : (
          <div className="events-list">
            {upcomingEvents.map((event) => (
              <div key={event.id} className="mini-event-item">
                <div className="event-icon-wrapper">
                  {event.icon}
                </div>
                <div className="event-details">
                  <div className="event-title">{event.title}</div>
                  <div className="event-time">
                    {formatEventDate(event.datetime)}
                  </div>
                </div>
                <div className="event-countdown">
                  {getTimeUntilEvent(event.datetime)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MiniAgenda;