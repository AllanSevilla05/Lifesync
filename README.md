# LifeSync - AI-Powered Productivity Assistant

LifeSync is a full-stack application that helps you manage tasks, schedule optimization, and productivity tracking using AI assistance.

## Architecture

- **Backend**: FastAPI with SQLite database
- **Frontend**: React with Vite
- **Authentication**: JWT tokens
- **Database**: SQLite (development)

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd lifesync_ai_backend
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Start the backend server:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd life_sync_frontend
```

2. Powershell Execution policy:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Install dependencies:
```bash
npm install
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Tasks
- `GET /api/v1/tasks` - Get all tasks
- `POST /api/v1/tasks` - Create new task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/voice` - Create tasks from voice input
- `GET /api/v1/tasks/optimize/schedule` - Get AI-optimized schedule

## Usage

1. Start both backend and frontend servers
2. Open http://localhost:5173 in your browser
3. Create an account or login
4. Add tasks using the interface or voice input
5. Manage your tasks and view AI suggestions

## Development

### Backend Development
- FastAPI with automatic OpenAPI documentation at http://localhost:8000/docs
- SQLAlchemy ORM with SQLite database
- Pydantic for data validation
- JWT authentication

### Frontend Development
- React 19 with Vite
- React Router for navigation
- Context API for state management
- Lucide React for icons

## Troubleshooting

### Common Issues

1. **Frontend build errors**: Clear node_modules and reinstall
2. **Database errors**: Delete lifesync.db to reset database
3. **CORS issues**: Ensure backend is running on port 8000
4. **Authentication issues**: Clear localStorage and re-login

### Database Reset
```bash
cd lifesync_ai_backend
rm lifesync.db
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```