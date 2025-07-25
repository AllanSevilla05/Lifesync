import './Hero.css'

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <h1>Welcome to</h1>
          <h1 className='Title'>LifeSync</h1>
          <p>Where plans becomes progress</p>
          <button className="cta-button">Get Started</button>
        </div>
        <div className="hero-image">
          <div className="placeholder-image">🚀</div>
        </div>
      </div>
    </section>
  )
}

export default Hero