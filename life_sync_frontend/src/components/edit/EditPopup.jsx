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
} from "lucide-react";

const iconOptions = [
  {
    label: "Workout",
    value: "Workout",
    component: <Dumbbell size={24} color="#667eea" />,
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
    label: "Book",
    value: "Book",
    component: <Book size={24} color="#667eea" />,
  },
  {
    label: "Assignment",
    value: "Assignment",
    component: <FileText size={24} color="#667eea" />,
  },
  {
    label: "Exam",
    value: "Exam",
    component: <ClipboardCheck size={24} color="#667eea" />,
  },
  {
    label: "Study Session",
    value: "Study",
    component: <BookOpen size={24} color="#667eea" />,
  },
  {
    label: "Sleep",
    value: "Sleep",
    component: <Moon size={24} color="#667eea" />,
  },
  {
    label: "Hydration",
    value: "Hydration",
    component: <Droplet size={24} color="#667eea" />,
  },
  {
    label: "Break",
    value: "Break",
    component: <Coffee size={24} color="#667eea" />,
  },
  {
    label: "To-Do",
    value: "ToDo",
    component: <ListTodo size={24} color="#667eea" />,
  },
  {
    label: "Meeting",
    value: "Meeting",
    component: <Users size={24} color="#667eea" />,
  },
  {
    label: "Event",
    value: "Event",
    component: <CalendarHeart size={24} color="#667eea" />,
  },
  {
    label: "Call",
    value: "Call",
    component: <PhoneCall size={24} color="#667eea" />,
  },
  {
    label: "Project",
    value: "Project",
    component: <LayoutDashboard size={24} color="#667eea" />,
  },
  {
    label: "Chores",
    value: "Chores",
    component: <BrushCleaning size={24} color="#667eea" />,
  },
  {
    label: "Meditation",
    value: "Meditation",
    component: <Wind size={24} color="#667eea" />,
  },
  {
    label: "Class",
    value: "Class",
    component: <Notebook size={24} color="#667eea" />,
  },
];

const EditPopup = ({ notification, onSave, onCancel }) => {
  const [title, setTitle] = useState(notification.title);
  const [datetime, setDatetime] = useState(notification.datetime);
  const [selectedIcon, setSelectedIcon] = useState(notification.icon);

  const handleIconChange = (e) => {
    const found = iconOptions.find((i) => i.value === e.target.value);
    setSelectedIcon(found?.component);
  };

  const handleSave = () => {
    onSave({ ...notification, title, datetime, icon: selectedIcon });
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
      <select onChange={handleIconChange} defaultValue="">
        <option value="" disabled>
          Select an icon
        </option>
        {iconOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

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
