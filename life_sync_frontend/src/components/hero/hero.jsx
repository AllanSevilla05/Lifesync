import { useNavigate } from 'react-router-dom';
import './Hero.css'

const Hero = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
  navigate('/login');
}

  return (
    <section className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <h1>Welcome to</h1>
          <h1 className='Title'>LifeSync</h1>
          <p>Where plans becomes progress</p>
          <button onClick={handleLoginClick} className="cta-button">Get Started</button>
        </div>
        <div className="hero-image">
          <div className="placeholder-image">🚀</div>
        </div>
      </div>
    </section>
  )
}

export default Hero