import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import Login from "./pages/login";
import SignUp from "./pages/sign_up";
import MainApp from "./pages/main_app";
import ForgotPassword from "./pages/forgot_password";
import SettingsPage from "./pages/settings/settings";
import ProfileSettings from "./pages/settings/profile_settings";
import CalendarPage from "./pages/calendar/calendar";
import MoodCalendarPage from "./pages/mood_calendar/mood_calendar";
import AIInteractionLog from "./pages/ai_log/ai_log";
import AboutPage from "./pages/about/about";

import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/sign_up" element={<SignUp />} />
        <Route path="/main" element={<MainApp />} />
        <Route path="/forgotpassword" element={<ForgotPassword />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/profile-settings" element={<ProfileSettings />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/mood-calendar" element={<MoodCalendarPage />} />
        <Route path="/ai-log" element={<AIInteractionLog />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </Router>
  );
}

export default App;
