import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./forgot_password.css"; // reuse the same styles

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement forgot password logic (send reset email etc)
    alert(`Password reset link sent to ${email}`);
    navigate("/login"); // redirect back to login after submit
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Forgot Password</h1>
          <p>Enter your email to reset your password</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              required
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <button type="submit" className="login-button">
            Send Reset Link
          </button>
        </form>

        <div className="login-footer">
          <p>
            Remembered your password? <Link to="/login">Back to Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
