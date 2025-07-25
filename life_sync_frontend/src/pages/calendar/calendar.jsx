import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import { ArrowLeft, Plus, Dumbbell, BriefcaseMedical, Wind, Bell } from 'lucide-react';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './calendar.css';

const localizer = momentLocalizer(moment);

// Sample events data - you can replace this with your actual notifications data
const sampleEvents = [
  {
    id: 1,
    title: 'Gym session with John',
    start: new Date(2025, 6, 28, 19, 0), // July 28, 2025, 7:00 PM
    end: new Date(2025, 6, 28, 20, 30),   // July 28, 2025, 8:30 PM
    type: 'gym',
    icon: 'dumbbell'
  },
  {
    id: 2,
    title: 'Doctor appointment',
    start: new Date(2025, 6, 30, 9, 0),   // July 30, 2025, 9:00 AM
    end: new Date(2025, 6, 30, 10, 0),    // July 30, 2025, 10:00 AM
    type: 'medical',
    icon: 'medical'
  },
  {
    id: 3,
    title: 'Yoga class',
    start: new Date(2025, 7, 2, 6, 0),    // August 2, 2025, 6:00 AM
    end: new Date(2025, 7, 2, 7, 0),      // August 2, 2025, 7:00 AM
    type: 'fitness',
    icon: 'wind'
  },
  {
    id: 4,
    title: 'Team Meeting',
    start: new Date(2025, 7, 5, 14, 0),   // August 5, 2025, 2:00 PM
    end: new Date(2025, 7, 5, 15, 30),    // August 5, 2025, 3:30 PM
    type: 'work',
    icon: 'bell'
  },
  {
    id: 5,
    title: 'Lunch with Sarah',
    start: new Date(2025, 7, 8, 12, 0),   // August 8, 2025, 12:00 PM
    end: new Date(2025, 7, 8, 13, 30),    // August 8, 2025, 1:30 PM
    type: 'social',
    icon: 'bell'
  }
];

const CalendarPage = () => {
  const navigate = useNavigate();
  const [view, setView] = useState('month');
  const [date, setDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState(null);

  const handleBackClick = () => {
    navigate('/main');
  };

  const handleAddEvent = () => {
    // You can implement add event functionality here
    alert('Add new event - integrate with your existing add functionality');
  };

  const handleSelectEvent = (event) => {
    setSelectedEvent(event);
  };

  const handleCloseModal = () => {
    setSelectedEvent(null);
  };

  // Custom event component to show icons
  const EventComponent = ({ event }) => {
    const getIcon = (iconType) => {
      switch (iconType) {
        case 'dumbbell':
          return <Dumbbell size={14} />;
        case 'medical':
          return <BriefcaseMedical size={14} />;
        case 'wind':
          return <Wind size={14} />;
        default:
          return <Bell size={14} />;
      }
    };

    return (
      <div className="custom-event">
        <span className="event-icon">{getIcon(event.icon)}</span>
        <span className="event-title">{event.title}</span>
      </div>
    );
  };

  // Custom event style getter
  const eventStyleGetter = (event) => {
    let backgroundColor = '#667eea';
    let borderColor = '#5a67d8';

    switch (event.type) {
      case 'gym':
      case 'fitness':
        backgroundColor = '#10b981';
        borderColor = '#059669';
        break;
      case 'medical':
        backgroundColor = '#ef4444';
        borderColor = '#dc2626';
        break;
      case 'work':
        backgroundColor = '#8b5cf6';
        borderColor = '#7c3aed';
        break;
      case 'social':
        backgroundColor = '#f59e0b';
        borderColor = '#d97706';
        break;
      default:
        backgroundColor = '#667eea';
        borderColor = '#5a67d8';
    }

    return {
      style: {
        backgroundColor,
        borderColor,
        color: 'white',
        border: `2px solid ${borderColor}`,
        borderRadius: '6px',
        fontSize: '12px',
        fontWeight: '500'
      }
    };
  };

  const formats = useMemo(() => ({
    timeGutterFormat: 'HH:mm',
    eventTimeRangeFormat: ({ start, end }) => {
      return `${moment(start).format('HH:mm')} - ${moment(end).format('HH:mm')}`;
    },
    agendaTimeRangeFormat: ({ start, end }) => {
      return `${moment(start).format('HH:mm')} - ${moment(end).format('HH:mm')}`;
    },
  }), []);

  return (
    <div className="calendar-container">
      <div className="calendar-card">
        {/* Header */}
        <div className="calendar-header">
          <button 
            onClick={handleBackClick}
            className="back-button"
            aria-label="Go back to main page"
          >
            <ArrowLeft size={24} />
          </button>
          <h1>Calendar</h1>
          <button 
            onClick={handleAddEvent}
            className="add-event-button"
            aria-label="Add new event"
          >
            <Plus size={20} />
            Add Event
          </button>
        </div>



        {/* Calendar Component */}
        <div className="calendar-wrapper">
          <Calendar
            localizer={localizer}
            events={sampleEvents}
            startAccessor="start"
            endAccessor="end"
            style={{ height: 600 }}
            view={view}
            onView={setView}
            date={date}
            onNavigate={setDate}
            onSelectEvent={handleSelectEvent}
            eventPropGetter={eventStyleGetter}
            components={{
              event: EventComponent,
            }}
            formats={formats}
            step={30}
            showMultiDayTimes
            popup
            popupOffset={30}
          />
        </div>

        {/* Event Details Modal */}
        {selectedEvent && (
          <div className="event-modal-overlay" onClick={handleCloseModal}>
            <div className="event-modal" onClick={(e) => e.stopPropagation()}>
              <div className="event-modal-header">
                <h3>{selectedEvent.title}</h3>
                <button onClick={handleCloseModal} className="close-button">
                  ×
                </button>
              </div>
              <div className="event-modal-content">
                <p><strong>Start:</strong> {moment(selectedEvent.start).format('MMMM Do YYYY, h:mm A')}</p>
                <p><strong>End:</strong> {moment(selectedEvent.end).format('MMMM Do YYYY, h:mm A')}</p>
                <p><strong>Duration:</strong> {moment(selectedEvent.end).diff(moment(selectedEvent.start), 'hours', true)} hours</p>
                <p><strong>Type:</strong> {selectedEvent.type}</p>
              </div>
              <div className="event-modal-actions">
                <button onClick={() => alert('Edit functionality')}>Edit</button>
                <button onClick={() => alert('Delete functionality')}>Delete</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CalendarPage;