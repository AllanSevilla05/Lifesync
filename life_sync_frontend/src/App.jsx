import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { TasksProvider } from "./contexts/TasksContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { OfflineProvider } from "./contexts/OfflineContext";
import Home from "./pages/home";
import Login from "./pages/login";
import SignUp from "./pages/sign_up";
import MainApp from "./pages/main_app";
import ForgotPassword from "./pages/forgot_password";
import SettingsPage from "./pages/settings/settings";
import ProfileSettings from "./pages/settings/profile_settings";
import CalendarView from "./pages/calendar/CalendarView";
import Analytics from "./pages/analytics/Analytics";
import Onboarding from "./pages/onboarding/Onboarding";
import Teams from "./pages/teams/Teams";
import AIScheduling from "./pages/scheduling/AIScheduling";
import Goals from "./pages/goals/Goals";
import TimeTracking from "./pages/timetracking/TimeTracking";
import ProtectedRoute from "./components/ProtectedRoute";

import "./App.css";
import "./styles/themes.css";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <OfflineProvider>
          <TasksProvider>
            <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/sign_up" element={<SignUp />} />
          <Route path="/forgotpassword" element={<ForgotPassword />} />
          <Route 
            path="/main" 
            element={
              <ProtectedRoute>
                <MainApp />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile-settings" 
            element={
              <ProtectedRoute>
                <ProfileSettings />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/calendar" 
            element={
              <ProtectedRoute>
                <CalendarView />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/onboarding" 
            element={
              <ProtectedRoute>
                <Onboarding />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/teams" 
            element={
              <ProtectedRoute>
                <Teams />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/ai-scheduling" 
            element={
              <ProtectedRoute>
                <AIScheduling />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/goals" 
            element={
              <ProtectedRoute>
                <Goals />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/time-tracking" 
            element={
              <ProtectedRoute>
                <TimeTracking />
              </ProtectedRoute>
            } 
          />
        </Routes>
            </Router>
          </TasksProvider>
        </OfflineProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
