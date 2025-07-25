import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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
import MiniAgenda from "../../components/mini_agenda/mini_agenda";
import MoodTracker from "../../components/mood_tracker/mood_tracker";

import "./main_app.css";

const now = new Date();

const initialNotifications = {
  pastDue: [
    {
      id: 1,
      icon: <Dumbbell size={24} color="#667eea" />,
      title: "Gym session with John",
      datetime: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
        .toISOString()
        .slice(0, 16),
    },
    {
      id: 2,
      icon: <BriefcaseMedical size={24} color="#667eea" />,
      title: "Doctor appointment",
      datetime: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000) // 5 days ago
        .toISOString()
        .slice(0, 16),
    },
  ],
  comingUp: [
    {
      id: 3,
      icon: <Wind size={24} color="#667eea" />,
      title: "Yoga class",
      datetime: new Date(now.getTime() + 3 * 60 * 60 * 1000) // 3 hours later
        .toISOString()
        .slice(0, 16),
    },
  ],
};

const MainApp = () => {
  // All state declarations in one place
  const [searchText, setSearchText] = useState("");
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [showAiSuggestion, setShowAiSuggestion] = useState(true);
  const [notificationsData, setNotificationsData] = useState(initialNotifications);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [editingNotification, setEditingNotification] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);

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

  const handleDismiss = () => {
    setNotificationsData((prev) => {
      if (prev.pastDue.find((n) => n.id === menuOpenId)) {
        return {
          ...prev,
          pastDue: prev.pastDue.filter((n) => n.id !== menuOpenId),
        };
      }
      if (prev.comingUp.find((n) => n.id === menuOpenId)) {
        return {
          ...prev,
          comingUp: prev.comingUp.filter((n) => n.id !== menuOpenId),
        };
      }
      return prev;
    });
    setMenuOpenId(null);
  };

  const handleEdit = () => {
    const allNotifications = [
      ...notificationsData.pastDue,
      ...notificationsData.comingUp,
    ];
    const notif = allNotifications.find((n) => n.id === menuOpenId);
    if (notif) setEditingNotification(notif);
    setMenuOpenId(null);
  };

  const handleSettingsClick = () => {
    navigate('/settings');
    setProfileMenuOpen(false);
  };


  const handleViewCalendar = () => {
    navigate('/calendar');
  };

  const handleViewMoodCalendar = () => {
    navigate('/mood-calendar');
  };

  const handleViewAILog = () => {
    navigate('/ai-log');
    setProfileMenuOpen(false);
  };


  const handleAdd = () => {
    setIsAddingNew(true);
    setEditingNotification({
      id: null,
      icon: <Bell size={24} color="#667eea" />,
      title: "",
      datetime: new Date().toISOString().slice(0, 16),
    });
  };

  const handleSaveEdit = (updatedNotif) => {
    const nowISO = new Date().toISOString().slice(0, 16);
    const isPastDue = updatedNotif.datetime < nowISO;

    if (isAddingNew) {
      const allNotifications = [
        ...notificationsData.pastDue,
        ...notificationsData.comingUp,
      ];
      const maxId = allNotifications.reduce(
        (max, n) => (n.id > max ? n.id : max),
        0
      );
      updatedNotif.id = maxId + 1;

      setNotificationsData((prev) => ({
        pastDue: isPastDue ? [...prev.pastDue, updatedNotif] : prev.pastDue,
        comingUp: !isPastDue ? [...prev.comingUp, updatedNotif] : prev.comingUp,
      }));
      setIsAddingNew(false);
    } else {
      setNotificationsData((prev) => {
        const filteredPastDue = prev.pastDue.filter(
          (n) => n.id !== updatedNotif.id
        );
        const filteredComingUp = prev.comingUp.filter(
          (n) => n.id !== updatedNotif.id
        );

        return {
          pastDue: isPastDue
            ? [...filteredPastDue, updatedNotif]
            : filteredPastDue,
          comingUp: !isPastDue
            ? [...filteredComingUp, updatedNotif]
            : filteredComingUp,
        };
      });
    }
    setEditingNotification(null);
  };

  const handleCancelEdit = () => {
    setEditingNotification(null);
    setIsAddingNew(false);
  };

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
                 <button onClick={handleViewAILog}>AI Log</button>
                 <button onClick={handleSettingsClick}>Settings</button>
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
            onClick={() => alert(`Searching for: "${searchText}"`)}
          >
            <Search size={18} />
          </button>
          <button
            type="button"
            className="voice-button"
            aria-label="Voice search"
          >
            <Mic size={18} />
            Voice
          </button>
        </div>

        <div className="notifications">
          <div className="d-flex align-items-center justify-content-between add-task">
            <h2>Tasks</h2>
            <button className="add-task-button"
              type="button"
              aria-label="Add new task"
              onClick={() => handleAdd()}
            >
              <Plus size={18} /> New
            </button>
          </div>

          <div className="notification-list">
            <h3>Past Due</h3>
            {notificationsData.pastDue.length === 0 && <p>No past due items</p>}
            {notificationsData.pastDue.map(({ id, icon, title, datetime }) => (
              <div className="notification-item" key={id}>
                <div className="notification-left">
                  <div className="notification-icon">{icon}</div>
                  <div className="notification-text">
                    <div className="title">{title}</div>
                    <div className="time">{formatDatetime(datetime)}</div>
                  </div>
                </div>

                <button
                  className="menu-button"
                  onClick={() => toggleMenu(id)}
                  aria-label="Open menu"
                  ref={(el) => (menuRefs.current[id] = el)}
                >
                  <EllipsisVertical size={20} />
                </button>

                {menuOpenId === id && (
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
            {notificationsData.comingUp.length === 0 && (
              <p>No upcoming items</p>
            )}
            {notificationsData.comingUp.map(({ id, icon, title, datetime }) => (
              <div className="notification-item" key={id}>
                <div className="notification-left">
                  <div className="notification-icon">{icon}</div>
                  <div className="notification-text">
                    <div className="title">{title}</div>
                    <div className="time">{formatDatetime(datetime)}</div>
                  </div>
                </div>

                <button
                  className="menu-button"
                  onClick={() => toggleMenu(id)}
                  aria-label="Open menu"
                  ref={(el) => (menuRefs.current[id] = el)}
                >
                  <EllipsisVertical size={20} />
                </button>

                {menuOpenId === id && (
                  <div className="menu-popup show">
                    <button onClick={() => handleDismiss(id)}>Dismiss</button>
                    <button onClick={() => handleEdit(id)}>Edit</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <MiniAgenda 
          notificationsData={notificationsData}
          onViewCalendar={handleViewCalendar}
        />
        <MoodTracker onViewMoodCalendar={handleViewMoodCalendar} />

        <div className="buttons-section">
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
      {editingNotification && (
        <EditPopup
          notification={editingNotification}
          onSave={handleSaveEdit}
          onCancel={handleCancelEdit}
        />
      )}
    </div>
  );
};

export default MainApp;