import { useState } from "react";
import {
  Dumbbell,
  Bell,
  BriefcaseMedical,
  Book,
  FileText,
  ClipboardCheck,
  BookOpen,
  Moon,
  Droplet,
  Coffee,
  ListTodo,
  Users,
  CalendarHeart,
  PhoneCall,
  LayoutDashboard,
  BrushCleaning,
  Wind,
  Notebook,
  PawPrint,
  Car,
  ShoppingBasket,
} from "lucide-react";

const iconOptions = [
  {
    label: "Assignment",
    value: "Assignment",
    component: <FileText size={24} color="#667eea" />,
  },
  {
    label: "Break",
    value: "Break",
    component: <Coffee size={24} color="#667eea" />,
  },
  {
    label: "Book",
    value: "Book",
    component: <Book size={24} color="#667eea" />,
  },
  {
    label: "Call",
    value: "Call",
    component: <PhoneCall size={24} color="#667eea" />,
  },
  {
    label: "Chores",
    value: "Chores",
    component: <BrushCleaning size={24} color="#667eea" />,
  },
  {
    label: "Class",
    value: "Class",
    component: <Notebook size={24} color="#667eea" />,
  },
  {
    label: "Exam",
    value: "Exam",
    component: <ClipboardCheck size={24} color="#667eea" />,
  },
  {
    label: "Event",
    value: "Event",
    component: <CalendarHeart size={24} color="#667eea" />,
  },
  {
    label: "General",
    value: "General",
    component: <Bell size={24} color="#667eea" />,
  },
  {
    label: "Health",
    value: "Health",
    component: <BriefcaseMedical size={24} color="#667eea" />,
  },
  {
    label: "Hydration",
    value: "Hydration",
    component: <Droplet size={24} color="#667eea" />,
  },
  {
    label: "Meditation",
    value: "Meditation",
    component: <Wind size={24} color="#667eea" />,
  },
  {
    label: "Meeting",
    value: "Meeting",
    component: <Users size={24} color="#667eea" />,
  },
  {
    label: "Pickup",
    value: "Pickup",
    component: <Car size={24} color="#667eea" />,
  },
  {
    label: "Project",
    value: "Project",
    component: <LayoutDashboard size={24} color="#667eea" />,
  },
  {
    label: "Shopping",
    value: "Shopping",
    component: <ShoppingBasket size={24} color="#667eea" />,
  },
  {
    label: "Sleep",
    value: "Sleep",
    component: <Moon size={24} color="#667eea" />,
  },
  {
    label: "Study Session",
    value: "Study",
    component: <BookOpen size={24} color="#667eea" />,
  },
  {
    label: "To-Do",
    value: "ToDo",
    component: <ListTodo size={24} color="#667eea" />,
  },
  {
    label: "Vet",
    value: "Vet",
    component: <PawPrint size={24} color="#667eea" />,
  },
  {
    label: "Workout",
    value: "Workout",
    component: <Dumbbell size={24} color="#667eea" />,
  },
];

const EditPopup = ({ notification, onSave, onCancel }) => {
  const [title, setTitle] = useState(notification.title);
  const [datetime, setDatetime] = useState(notification.datetime);

  const initialSelectedValue =
    iconOptions.find((opt) => opt.component.type === notification.icon.type)
      ?.value || "";

  const [selectedIconValue, setSelectedIconValue] =
    useState(initialSelectedValue);

  const handleIconClick = (value) => {
    setSelectedIconValue(value);
  };

  const handleSave = () => {
    const selectedIconObj = iconOptions.find(
      (opt) => opt.value === selectedIconValue
    );
    onSave({
      ...notification,
      title,
      datetime,
      icon: selectedIconObj?.component || notification.icon,
    });
  };

  return (
    <div className="edit-popup">
      <h4>Edit Notification</h4>

      <label>Title</label>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />

      <label>Date & Time</label>
      <input
        type="datetime-local"
        value={datetime}
        onChange={(e) => setDatetime(e.target.value)}
      />

      <label>Icon</label>
      <div
        style={{
          display: "flex",
          overflowX: "auto",
          gap: "12px",
          padding: "8px 0",
          border: "1px solid #ccc",
          borderRadius: "4px",
          whiteSpace: "nowrap",
        }}
      >
        {iconOptions.map(({ label, value, component }) => (
          <button
            key={value}
            type="button"
            onClick={() => handleIconClick(value)}
            title={label}
            style={{
              cursor: "pointer",
              border:
                selectedIconValue === value
                  ? "2px solid #667eea"
                  : "2px solid transparent",
              borderRadius: "6px",
              background: "none",
              padding: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              minWidth: "40px",
              minHeight: "40px",
              flexShrink: 0,
              transition: "border-color 0.3s",
            }}
          >
            {component}
          </button>
        ))}
      </div>

      <div className="edit-popup-buttons">
        <button onClick={handleSave}>Save</button>
        <button onClick={onCancel} className="cancel-btn">
          Cancel
        </button>
      </div>
    </div>
  );
};

export default EditPopup;
