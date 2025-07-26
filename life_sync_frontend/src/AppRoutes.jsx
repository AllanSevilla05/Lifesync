import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Import your page components
import Login from './pages/login';
import SignUp from './pages/sign_up';
import Home from './pages/home';
import MainApp from './pages/main_app';
import Calendar from './pages/calendar';
import MoodCalendar from './pages/mood_calendar';
import AILog from './pages/ai_log';
import About from './pages/about';
import Settings from './pages/settings';
import ForgotPassword from './pages/forgot_password';

// Protected Route component
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    
    if (loading) {
        return <div>Loading...</div>;
    }
    
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    
    return children;
};

const AppRoutes = () => {
    return (
        <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/sign-up" element={<SignUp />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/about" element={<About />} />
            
            {/* Protected routes - require authentication */}
            <Route 
                path="/main-app" 
                element={
                    <ProtectedRoute>
                        <MainApp />
                    </ProtectedRoute>
                } 
            />
            <Route 
                path="/calendar" 
                element={
                    <ProtectedRoute>
                        <Calendar />
                    </ProtectedRoute>
                } 
            />
            <Route 
                path="/mood-calendar" 
                element={
                    <ProtectedRoute>
                        <MoodCalendar />
                    </ProtectedRoute>
                } 
            />
            <Route 
                path="/ai-log" 
                element={
                    <ProtectedRoute>
                        <AILog />
                    </ProtectedRoute>
                } 
            />
            <Route 
                path="/settings" 
                element={
                    <ProtectedRoute>
                        <Settings />
                    </ProtectedRoute>
                } 
            />
            
            {/* Catch all route - redirect to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};

export default AppRoutes; 