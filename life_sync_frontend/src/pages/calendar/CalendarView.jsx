import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Calendar from '../../components/calendar/Calendar';
import EditPopup from '../../components/edit/EditPopup';
import { useTasks } from '../../contexts/TasksContext';
import './CalendarView.css';

const CalendarView = () => {
  const navigate = useNavigate();
  const { createTask } = useTasks();
  const [selectedDate, setSelectedDate] = useState(null);
  const [isCreatingTask, setIsCreatingTask] = useState(false);
  const [newTask, setNewTask] = useState(null);

  const handleDateSelect = (date) => {
    setSelectedDate(date);
  };

  const handleTaskCreate = (date) => {
    const taskDateTime = new Date(date);
    taskDateTime.setHours(9, 0, 0, 0); // Default to 9 AM
    
    setNewTask({
      id: null,
      title: "",
      description: "",
      datetime: taskDateTime.toISOString().slice(0, 16),
      priority: 3,
      status: "pending"
    });
    setIsCreatingTask(true);
  };

  const handleSaveTask = async (taskData) => {
    const result = await createTask({
      title: taskData.title,
      description: taskData.description || "",
      due_date: taskData.datetime ? new Date(taskData.datetime).toISOString() : null,
      priority: taskData.priority || 3,
      status: taskData.status || "pending"
    });

    if (result.success) {
      setIsCreatingTask(false);
      setNewTask(null);
    } else {
      console.error('Failed to create task:', result.error);
    }
  };

  const handleCancelTask = () => {
    setIsCreatingTask(false);
    setNewTask(null);
  };

  return (
    <div className="calendar-view">
      {/* Header */}
      <div className="calendar-view-header">
        <button 
          onClick={() => navigate('/main')}
          className="back-button"
          aria-label="Back to main app"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        <h1>Calendar View</h1>
      </div>

      {/* Calendar Component */}
      <div className="calendar-wrapper">
        <Calendar 
          onDateSelect={handleDateSelect}
          onTaskCreate={handleTaskCreate}
        />
      </div>

      {/* Task Creation Modal */}
      {isCreatingTask && newTask && (
        <EditPopup
          notification={newTask}
          onSave={handleSaveTask}
          onCancel={handleCancelTask}
        />
      )}
    </div>
  );
};

export default CalendarView;