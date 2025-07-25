import './Features.css'

const Features = () => {
  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Smart Scheduling',
      description: 'Advanced AI learns your habits and preferences to automatically optimize your daily schedule and suggest the best times for tasks.'
    },
    {
      icon: '🎯',
      title: 'Dynamic Task Prioritization',
      description: 'Intelligent priority algorithms automatically rank your tasks by urgency, importance, and deadlines to keep you focused on what matters most.'
    },
    {
      icon: '🎤',
      title: 'Voice Command Integration',
      description: 'Simply say "LifeSync, I need to shop, exercise, and work on my business proposal" and watch your tasks get organized instantly.'
    },
    {
      icon: '📊',
      title: 'Mood & Energy Tracking',
      description: 'Track your mood and energy levels to receive personalized wellness suggestions and optimize task scheduling for peak performance.'
    },
    {
      icon: '📚',
      title: 'Document Processing',
      description: 'Upload syllabi, schedules, or documents and automatically generate tasks, deadlines, and reminders with intelligent parsing.'
    },
    {
      icon: '🔄',
      title: 'Real-Time Adaptability',
      description: 'Smart rescheduling system automatically adjusts your calendar when delays or conflicts arise, keeping you on track effortlessly.'
    },
    {
      icon: '📱',
      title: 'Progress Check-ins',
      description: 'Receive timely check-ins like "Did you start your workout?" with AI feedback loops that improve scheduling accuracy over time.'
    },
    {
      icon: '💡',
      title: 'Habit-Based Learning',
      description: 'LifeSync learns from your behavior patterns and productivity windows to suggest optimal scheduling and personalized routines.'
    }
  ]

  return (
    <section className="features">
      <div className="features-container">
        <h2>Why Choose Our Solution?</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Features