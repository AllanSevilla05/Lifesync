import { useState } from "react";
import { Link } from "react-router-dom";
import "./main_app.css";

const MainApp = () => {
  return (
    <div className="signup-container">
      <div className="signup-card">
        <div className="signup-header d-flex flex-column">
          <img src="/images/LifeSyncLogo.png" alt="Logo" />
          <h1>MAIN APP</h1>
          <p>Join LifeSync and organize your life</p>
        </div>
      </div>
    </div>
  );
};

export default MainApp;
