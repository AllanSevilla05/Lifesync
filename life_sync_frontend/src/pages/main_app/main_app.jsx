import { useState, useRef, useEffect } from "react";
import {
  Mic,
  EllipsisVertical,
  Calendar,
  Activity,
  Dumbbell,
  Bell,
} from "lucide-react";
import "./main_app.css";

const initialNotifications = {
  pastDue: [
    {
      id: 1,
      icon: <Dumbbell size={24} color="#667eea" />,
      title: "Gym session with John",
      time: "Reminder set for: July 5th, 2025 at 7:00PM",
    },
    {
      id: 2,
      icon: <Bell size={24} color="#667eea" />,
      title: "Doctor appointment",
      time: "Reminder set for: July 1st, 2025 at 9:00AM",
    },
  ],
  comingUp: [
    {
      id: 3,
      icon: <Dumbbell size={24} color="#667eea" />,
      title: "Yoga class",
      time: "Reminder set for: July 10th, 2025 at 6:00AM",
    },
  ],
};

const MainApp = () => {
  const [searchText, setSearchText] = useState("");
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [showAiSuggestion, setShowAiSuggestion] = useState(true);
  const [notificationsData, setNotificationsData] =
    useState(initialNotifications);

  const menuRefs = useRef({});

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
      }, 500); // delay allows the menu button click to fire first
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpenId]);

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
    alert(`Edit notification ${menuOpenId}`);
    setMenuOpenId(null);
  };

  return (
    <div className="main-container">
      <div className="main-card">
        <div className="main-header d-flex flex-column">
          <img src="/images/LifeSyncLogo.png" alt="Logo" className="mx-auto" />
        </div>

        <div className="search-bar">
          <input
            type="text"
            placeholder="Got something coming up? Let me know!"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <button type="button" aria-label="Voice search">
            <Mic size={18} />
            Voice
          </button>
        </div>

        <div className="notifications">
          <h2>Notifications</h2>

          <div className="notification-list">
            <h3>Past Due</h3>
            {notificationsData.pastDue.length === 0 && <p>No past due items</p>}
            {notificationsData.pastDue.map(({ id, icon, title, time }) => (
              <div className="notification-item" key={id}>
                <div className="notification-left">
                  <div className="notification-icon">{icon}</div>
                  <div className="notification-text">
                    <div className="title">{title}</div>
                    <div className="time">{time}</div>
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
            {notificationsData.comingUp.map(({ id, icon, title, time }) => (
              <div className="notification-item" key={id}>
                <div className="notification-left">
                  <div className="notification-icon">{icon}</div>
                  <div className="notification-text">
                    <div className="title">{title}</div>
                    <div className="time">{time}</div>
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
    </div>
  );
};

export default MainApp;
