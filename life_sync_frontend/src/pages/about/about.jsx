import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Heart, 
  Calendar, 
  Bot, 
  TrendingUp, 
  Users, 
  Shield, 
  Sparkles,
  Mail,
  MapPin,
  Phone,
  ExternalLink,
  Star
} from 'lucide-react';
import './about.css'; 
import { Header, Footer } from '../../components';

const AboutPage = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate('/');
  };

  const team = [
    {
      name: "Monet Chisholm",
    },
    {
      name: "Leonardo Cruz",
    },
    {
      name: "Sofia Di Lorenzo",
    },
    {
      name: "Allan Sevilla",
    },
    {
        name: "Steven Velasquez"
    }
  ];

  return (
    <div className="about-container">
        <Header />
        <div className="about-content">
          {/* Hero Section */}
          <section className="hero-section">
            <div className="hero-logo">
              <img src="/images/LifeSyncLogo.png" alt="LifeSync Logo" className="logo-large" />
            </div>
            <h2>Your Personal Life Management Assistant</h2>
            <p className="hero-description">
              LifeSync is designed to help you achieve the perfect balance between productivity and well-being. 
              Our intelligent platform combines calendar management, mood tracking, and AI-powered insights 
              to help you live your best life.
            </p>
          </section>

          {/* Mission Section */}
          <section className="mission-section">
            <div className="section-header">
              <Sparkles size={24} />
              <h3>Our Mission</h3>
            </div>
            <p>
              As college students, we understand the challenges of balancing academics, social life, and personal well-being.
              Our mission is to provide a comprehensive solution that empowers you to manage your time effectively, reduce stress, and enhance your overall quality of life
              through the use of innovative technology and user-friendly design.
            </p>
          </section>

          {/* Team Section */}
          <section className="team-section">
            <div className="section-header">
              <Users size={24} />
              <h3>Meet Our Team</h3>
            </div>
            <div className="team-grid">
              {team.map((member, index) => (
                <div key={index} className="team-member">
                  <div className="member-avatar">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <h4>{member.name}</h4>
                  <p className="member-role">{member.role}</p>
                  <p className="member-bio">{member.bio}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Values Section */}
          <section className="values-section">
            <div className="section-header">
              <Shield size={24} />
              <h3>Our Values</h3>
            </div>
            <div className="values-grid">
              <div className="value-item">
                <h4>Privacy First</h4>
                <p>Your data is yours. We use industry-leading security measures to protect your personal information.</p>
              </div>
              <div className="value-item">
                <h4>User-Centric Design</h4>
                <p>Every feature is designed with you in mind, focusing on simplicity and effectiveness.</p>
              </div>
              <div className="value-item">
                <h4>Continuous Innovation</h4>
                <p>We're constantly improving and adding new features based on user feedback and emerging technologies.</p>
              </div>
              <div className="value-item">
                <h4>Holistic Wellness</h4>
                <p>We believe in supporting not just productivity, but overall mental and emotional well-being.</p>
              </div>
            </div>
          </section>
      </div>
      <Footer />
    </div>
  );
};

export default AboutPage;