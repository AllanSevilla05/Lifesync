import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import Login from "./pages/login";
import SignUp from "./pages/sign_up";
import MainApp from "./pages/main_app";
import ForgotPassword from "./pages/forgot_password";
import SettingsPage from "./pages/settings/settings";
import ProfileSettings from "./pages/settings/profile_settings";

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
      </Routes>
    </Router>
  );
}

export default App;
