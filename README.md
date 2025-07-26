# LifeSync

LifeSync is an AI-powered productivity and wellness assistant that helps you manage tasks, track moods, and maintain your overall well-being. It combines modern web technologies with intelligent AI services to provide a comprehensive life management platform.

## Project Structure

```
Lifesync/
├── life_sync_frontend/          # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── header/          # Navigation header
│   │   │   ├── footer/          # Site footer
│   │   │   ├── hero/            # Landing page hero section
│   │   │   ├── features/        # Feature showcase
│   │   │   ├── mini_agenda/     # Compact task view
│   │   │   └── mood_tracker/    # Mood tracking component
│   │   ├── pages/               # Application pages
│   │   │   ├── home/            # Landing page
│   │   │   ├── main_app/        # Main dashboard
│   │   │   ├── calendar/        # Calendar view
│   │   │   ├── mood_calendar/   # Mood tracking calendar
│   │   │   ├── ai_log/          # AI interaction history
│   │   │   ├── settings/        # User settings
│   │   │   ├── login/           # Authentication
│   │   │   └── sign_up/         # User registration
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Vite build configuration
├── lifesync_ai_backend/         # FastAPI backend
│   ├── app/
│   │   ├── api/v1/              # API routes
│   │   ├── core/                # Core configuration
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── pyproject.toml           # Python dependencies
│   └── main.py                  # Application entry point
└── README.md                    # This file
```

## Prerequisites

Before running the application, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (3.11 or higher) - [Download](https://python.org/)
- **PostgreSQL** (v12 or higher) - [Download](https://postgresql.org/)
- **Redis** (v6 or higher) - [Download](https://redis.io/)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Lifesync
```

### 2. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd lifesync_ai_backend
   ```

2. **Install Python dependencies using uv (recommended) or pip:**
   ```bash
   # Using uv (faster)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `lifesync_ai_backend` directory:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/lifesync
   
   # Security
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # AI Services - Local Ollama with Llama3
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   
   # Redis
   REDIS_URL=redis://localhost:6379
   
   # File Upload
   UPLOAD_DIR=uploads
   MAX_FILE_SIZE=10485760
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # Create database (adjust credentials as needed)
   createdb lifesync
   ```

5. **Start Redis server:**
   ```bash
   redis-server
   ```

6. **Run the backend server:**
   ```bash
   # Using uv
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend API will be available at: http://localhost:8000

### 3. Frontend Setup

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd life_sync_frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:5173

## Available Scripts

### Frontend (life_sync_frontend/)
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend (lifesync_ai_backend/)
- `uvicorn app.main:app --reload` - Start development server
- `pytest` - Run tests
- `alembic upgrade head` - Run database migrations

## API Documentation

Once the backend is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Features

- **Task Management**: Create, organize, and track your daily tasks  
- **Mood Tracking**: Monitor your emotional well-being over time  
- **AI Integration**: Get intelligent suggestions and insights  
- **Analytics Dashboard**: Visualize your productivity and mood patterns  
- **User Authentication**: Secure login and user management  
- **Responsive Design**: Works on desktop and mobile devices  

## Technology Stack

### Frontend
- **React** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Bootstrap** - UI framework
- **React Big Calendar** - Calendar component
- **Lucide React** - Icon library
- **Moment.js** - Date manipulation

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Uvicorn** - ASGI server

## Database Setup

1. **Install PostgreSQL** and create a database:
   ```sql
   Go to new terminal and input "psql -U postgres"
   Input password for Postgres used when downloading Postgres
   Once Postgres is open input:
      CREATE DATABASE lifesync;
      CREATE USER lifesync_user WITH PASSWORD 'your_password';
      GRANT ALL PRIVILEGES ON DATABASE lifesync TO lifesync_user;
   ```

2. **Update the DATABASE_URL** in your `.env` file:
   ```
   DATABASE_URL=postgresql://lifesync_user:your_password@localhost:5432/lifesync
   ```

3. **The database tables will be created automatically** when you start the backend server.

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the `lifesync_ai_backend` directory with these variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/lifesync

# Security
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services - Local Ollama with Llama3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Redis
REDIS_URL=redis://localhost:6379

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process on port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Kill process on port 5173
   lsof -ti:5173 | xargs kill -9
   ```

2. **Database connection errors:**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists

3. **Redis connection errors:**
   - Ensure Redis server is running: `redis-server`
   - Check Redis URL in configuration

4. **Frontend API calls failing:**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend

### Logs and Debugging

- **Backend logs**: Check the terminal where uvicorn is running
- **Frontend logs**: Check browser developer console
- **Database logs**: Check PostgreSQL logs for connection issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please create an issue in the repository or contact the development team.
