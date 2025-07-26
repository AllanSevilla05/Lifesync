import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { useTasks } from '../../contexts/TasksContext';
import './Calendar.css';

const Calendar = ({ onDateSelect, onTaskCreate }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState([]);
  const { tasks } = useTasks();

  // Generate calendar days
  useEffect(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const firstDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfWeek; i++) {
      const prevDate = new Date(year, month, -firstDayOfWeek + i + 1);
      days.push({
        date: prevDate,
        isCurrentMonth: false,
        tasks: getTasksForDate(prevDate)
      });
    }
    
    // Add days of the current month
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      days.push({
        date,
        isCurrentMonth: true,
        tasks: getTasksForDate(date)
      });
    }
    
    // Add empty cells for days after the last day of the month
    const remainingCells = 42 - days.length; // 6 weeks * 7 days
    for (let i = 1; i <= remainingCells; i++) {
      const nextDate = new Date(year, month + 1, i);
      days.push({
        date: nextDate,
        isCurrentMonth: false,
        tasks: getTasksForDate(nextDate)
      });
    }
    
    setCalendarDays(days);
  }, [currentDate, tasks]);

  const getTasksForDate = (date) => {
    const dateString = date.toDateString();
    return tasks.filter(task => {
      if (!task.due_date) return false;
      const taskDate = new Date(task.due_date);
      return taskDate.toDateString() === dateString;
    });
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + direction);
      return newDate;
    });
  };

  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isSelected = (date) => {
    return date.toDateString() === selectedDate.toDateString();
  };

  const handleDateClick = (date) => {
    setSelectedDate(date);
    if (onDateSelect) {
      onDateSelect(date);
    }
  };

  const getTaskStatusColor = (task) => {
    if (task.status === 'completed') return '#22c55e';
    if (task.status === 'in_progress') return '#f59e0b';
    if (task.priority >= 4) return '#ef4444';
    return '#6b7280';
  };

  const formatMonthYear = (date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    });
  };

  return (
    <div className="calendar-container">
      {/* Calendar Header */}
      <div className="calendar-header">
        <h2>{formatMonthYear(currentDate)}</h2>
        <div className="calendar-nav">
          <button 
            onClick={() => navigateMonth(-1)}
            className="nav-button"
            aria-label="Previous month"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="today-button"
          >
            Today
          </button>
          <button 
            onClick={() => navigateMonth(1)}
            className="nav-button"
            aria-label="Next month"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Days of Week Header */}
      <div className="weekdays-header">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="weekday-label">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="calendar-grid">
        {calendarDays.map((dayData, index) => (
          <div
            key={index}
            className={`calendar-day ${
              !dayData.isCurrentMonth ? 'other-month' : ''
            } ${
              isToday(dayData.date) ? 'today' : ''
            } ${
              isSelected(dayData.date) ? 'selected' : ''
            }`}
            onClick={() => handleDateClick(dayData.date)}
          >
            <div className="day-number">
              {dayData.date.getDate()}
            </div>
            
            {/* Task indicators */}
            <div className="task-indicators">
              {dayData.tasks.slice(0, 3).map((task, taskIndex) => (
                <div
                  key={task.id}
                  className="task-indicator"
                  style={{ backgroundColor: getTaskStatusColor(task) }}
                  title={task.title}
                />
              ))}
              {dayData.tasks.length > 3 && (
                <div className="task-indicator overflow-indicator">
                  +{dayData.tasks.length - 3}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Selected Date Details */}
      {selectedDate && (
        <div className="selected-date-details">
          <div className="details-header">
            <h3>{selectedDate.toLocaleDateString('en-US', { 
              weekday: 'long',
              month: 'long', 
              day: 'numeric',
              year: 'numeric'
            })}</h3>
            <button
              onClick={() => onTaskCreate && onTaskCreate(selectedDate)}
              className="add-task-button"
              aria-label="Add task for selected date"
            >
              <Plus size={16} /> Add Task
            </button>
          </div>
          
          <div className="date-tasks">
            {getTasksForDate(selectedDate).length === 0 ? (
              <p className="no-tasks">No tasks scheduled for this date</p>
            ) : (
              getTasksForDate(selectedDate).map(task => (
                <div key={task.id} className="date-task-item">
                  <div 
                    className="task-status-dot"
                    style={{ backgroundColor: getTaskStatusColor(task) }}
                  />
                  <div className="task-details">
                    <div className="task-title">{task.title}</div>
                    <div className="task-time">
                      {task.due_date ? 
                        new Date(task.due_date).toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit'
                        }) : 'No time set'
                      }
                    </div>
                  </div>
                  <div className={`task-priority priority-${task.priority}`}>
                    P{task.priority}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;