import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useTasks } from "../../contexts/TasksContext";
import {
  Mic,
  Search,
  EllipsisVertical,
  Calendar,
  Activity,
  Dumbbell,
  BriefcaseMedical,
  Wind,
  Plus,
  Bell,
  Heart,
} from "lucide-react";
import EditPopup from "../../components/edit/EditPopup";

import "./main_app.css";


const MainApp = () => {
  const { logout } = useAuth();
  const { 
    tasks, 
    loading: tasksLoading, 
    createTask, 
    updateTask, 
    deleteTask,
    getPastDueTasks,
    getUpcomingTasks,
    createTasksFromVoice 
  } = useTasks();

  // All state declarations in one place
  const [searchText, setSearchText] = useState("");
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [showAiSuggestion, setShowAiSuggestion] = useState(true);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);

  const menuRefs = useRef({});
  const profileMenuRef = useRef(null);
  const navigate = useNavigate();

  const formatDatetime = (dtString) =>
    `Reminder set for: ${new Date(dtString).toLocaleString()}`;

  useEffect(() => {
    const handleClickOutside = (event) => {
      setTimeout(() => {
        if (
          menuOpenId !== null &&
          menuRefs.current[menuOpenId] &&
          !menuRefs.current[menuOpenId].contains(event.target)
        ) {
          setMenuOpenId(null);
        }
      }, 500);
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpenId]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(event.target)
      ) {
        setProfileMenuOpen(false);
      }
    }
    if (profileMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [profileMenuOpen]);

  const toggleMenu = (id) => {
    setMenuOpenId(menuOpenId === id ? null : id);
  };

  const handleDismiss = async () => {
    if (menuOpenId) {
      await deleteTask(menuOpenId);
      setMenuOpenId(null);
    }
  };

  const handleEdit = () => {
    const task = tasks.find((t) => t.id === menuOpenId);
    if (task) {
      setEditingTask({
        ...task,
        icon: getTaskIcon(task),
        datetime: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : ""
      });
    }
    setMenuOpenId(null);
  };

  const getTaskIcon = (task) => {
    // Simple icon mapping based on task title/description
    const title = task.title?.toLowerCase() || '';
    if (title.includes('gym') || title.includes('workout')) return <Dumbbell size={24} color="#667eea" />;
    if (title.includes('doctor') || title.includes('appointment')) return <BriefcaseMedical size={24} color="#667eea" />;
    if (title.includes('yoga') || title.includes('meditation')) return <Wind size={24} color="#667eea" />;
    return <Bell size={24} color="#667eea" />;
  };

  const handleSettingsClick = () => {
    navigate('/settings');
    setProfileMenuOpen(false);
  };

  const handleAdd = () => {
    setIsAddingNew(true);
    setEditingTask({
      id: null,
      title: "",
      description: "",
      icon: <Bell size={24} color="#667eea" />,
      datetime: new Date().toISOString().slice(0, 16),
      priority: 1,
      status: "pending"
    });
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
    setProfileMenuOpen(false);
  };

  const handleSaveEdit = async (updatedTask) => {
    const taskData = {
      title: updatedTask.title,
      description: updatedTask.description || "",
      due_date: updatedTask.datetime ? new Date(updatedTask.datetime).toISOString() : null,
      priority: updatedTask.priority || 1,
      status: updatedTask.status || "pending"
    };

    let result;
    if (isAddingNew) {
      result = await createTask(taskData);
      setIsAddingNew(false);
    } else {
      result = await updateTask(updatedTask.id, taskData);
    }

    if (result.success) {
      setEditingTask(null);
    } else {
      // Handle error - you might want to show a toast notification
      console.error('Failed to save task:', result.error);
    }
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
    setIsAddingNew(false);
  };

  const handleVoiceSearch = async () => {
    if (!searchText.trim()) return;
    
    setIsProcessingVoice(true);
    const result = await createTasksFromVoice(searchText);
    
    if (result.success) {
      setSearchText("");
      // Show success message or handle the created tasks
    } else {
      console.error('Failed to process voice input:', result.error);
    }
    setIsProcessingVoice(false);
  };

  // Get categorized tasks
  const pastDueTasks = getPastDueTasks();
  const upcomingTasks = getUpcomingTasks();

  return (
    <div className="main-container">
      <div className="main-card">
        <div className="main-header">
          <div className="header-logo">
            <img src="/images/LifeSyncLogo.png" alt="LifeSync Logo" />
          </div>
          <div className="header-profile" ref={profileMenuRef}>
            <button
              className="profile-pic-btn"
              onClick={() => setProfileMenuOpen((open) => !open)}
              aria-label="Open profile menu"
              style={{ background: "none", border: "none", padding: 0, cursor: "pointer" }}
            >
              <img
                src="life_sync_frontend/src/assets/ProfilePicture.png"
                alt="Profile"
                className="profile-pic"
              />
            </button>
            {profileMenuOpen && (
              <div className="profile-dropdown">
                <button onClick={handleSettingsClick}>Settings</button>
                <button onClick={handleLogout}>Logout</button>
              </div>
            )}
          </div>
        </div>

        <div className="search-bar position-relative">
          <input
            type="text"
            placeholder="Got something coming up? Let me know!"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <button
            type="button"
            className="position-absolute "
            aria-label="Search"
            style={{ right: "113px", top: "6px" }}
            onClick={handleVoiceSearch}
            disabled={isProcessingVoice}
          >
            <Search size={18} />
          </button>
          <button
            type="button"
            className="voice-button"
            aria-label="Voice search"
            onClick={handleVoiceSearch}
            disabled={isProcessingVoice}
          >
            <Mic size={18} />
            {isProcessingVoice ? 'Processing...' : 'Voice'}
          </button>
        </div>

        <div className="notifications">
          <div className="d-flex align-items-center justify-content-between add-task">
            <h2>Notifications</h2>
            <button
              type="button"
              aria-label="Add new task"
              onClick={() => handleAdd()}
            >
              <Plus size={18} /> New
            </button>
          </div>

          <div className="notification-list">
            <h3>Past Due</h3>
            {tasksLoading && <p>Loading tasks...</p>}
            {!tasksLoading && pastDueTasks.length === 0 && <p>No past due items</p>}
            {!tasksLoading && pastDueTasks.map((task) => (
              <div className="notification-item" key={task.id}>
                <div className="notification-left">
                  <div className="notification-icon">{getTaskIcon(task)}</div>
                  <div className="notification-text">
                    <div className="title">{task.title}</div>
                    <div className="time">{task.due_date ? formatDatetime(task.due_date) : 'No due date'}</div>
                  </div>
                </div>

                <button
                  className="menu-button"
                  onClick={() => toggleMenu(task.id)}
                  aria-label="Open menu"
                  ref={(el) => (menuRefs.current[task.id] = el)}
                >
                  <EllipsisVertical size={20} />
                </button>

                {menuOpenId === task.id && (
                  <div className="menu-popup show">
                    <button onClick={() => handleDismiss()}>Dismiss</button>
                    <button onClick={() => handleEdit()}>Edit</button>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="notification-list">
            <h3>Coming Up</h3>
            {!tasksLoading && upcomingTasks.length === 0 && (
              <p>No upcoming items</p>
            )}
            {!tasksLoading && upcomingTasks.map((task) => (
              <div className="notification-item" key={task.id}>
                <div className="notification-left">
                  <div className="notification-icon">{getTaskIcon(task)}</div>
                  <div className="notification-text">
                    <div className="title">{task.title}</div>
                    <div className="time">{task.due_date ? formatDatetime(task.due_date) : 'No due date'}</div>
                  </div>
                </div>

                <button
                  className="menu-button"
                  onClick={() => toggleMenu(task.id)}
                  aria-label="Open menu"
                  ref={(el) => (menuRefs.current[task.id] = el)}
                >
                  <EllipsisVertical size={20} />
                </button>

                {menuOpenId === task.id && (
                  <div className="menu-popup show">
                    <button onClick={() => handleDismiss()}>Dismiss</button>
                    <button onClick={() => handleEdit()}>Edit</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="buttons-section">
          <button type="button" aria-label="View Calendar">
            <Calendar size={20} />
            View Calendar
          </button>
          <button type="button" aria-label="Productivity">
            <Activity size={20} />
            Productivity
          </button>
        </div>

        {showAiSuggestion && (
          <div className="ai-suggestion">
            <button
              className="ai-close-btn"
              aria-label="Close AI suggestion"
              onClick={() => setShowAiSuggestion(false)}
            >
              &times;
            </button>
            <h2>AI Suggestion</h2>
            <p className="ai-text">
              You are most productive in the morning. Would you like to change
              your gym session for tomorrow morning?
            </p>
          </div>
        )}
      </div>
      {editingTask && (
        <EditPopup
          notification={editingTask}
          onSave={handleSaveEdit}
          onCancel={handleCancelEdit}
        />
      )}
    </div>
  );
};

export default MainApp;