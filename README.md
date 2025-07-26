# LifeSync - Task Management App with Voice Input

A simple task management app that lets you create tasks using your voice! Built with React and Python.

## 📋 Prerequisites (Install These First!)

Before you can run the app, you need to install some software. Follow these steps:

### 1. Install Node.js (Required for Frontend)
**Download from**: https://nodejs.org/

1. Go to https://nodejs.org/
2. Click the big green "LTS" button (recommended)
3. Run the installer you downloaded
4. **Verify installation**: Open terminal and type:
   ```bash
   node --version
   npm --version
   ```
   You should see version numbers (like `v18.17.0` and `9.6.7`)

### 2. Install Python (Required for Backend)
**Download from**: https://www.python.org/downloads/

1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python" button
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Run the installer
5. **Verify installation**: Open terminal and type:
   ```bash
   python --version
   ```
   You should see a version number (like `Python 3.11.5`)

### 3. Install uv (Python Package Manager)
**Download from**: https://docs.astral.sh/uv/getting-started/installation/

1. Go to https://docs.astral.sh/uv/getting-started/installation/
2. Copy the installation command for your system:

   **For Mac/Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **For Windows:**
   ```bash
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Verify installation**: Open terminal and type:
   ```bash
   uv --version
   ```
   You should see a version number (like `uv 0.1.0`)

### 4. Install PostgreSQL (Database)
**Download from**: https://www.postgresql.org/download/

1. Go to https://www.postgresql.org/download/
2. Click your operating system:
   - **Windows**: Download from EnterpriseDB
   - **Mac**: Download from EnterpriseDB or use Homebrew
   - **Linux**: Use your package manager

3. **For Mac users with Homebrew:**
   ```bash
   brew install postgresql
   brew services start postgresql
   ```

4. **For Windows/Linux**: Follow the installer instructions
5. **Verify installation**: Open terminal and type:
   ```bash
   psql --version
   ```
   You should see a version number

### 5. Install Git (Version Control)
**Download from**: https://git-scm.com/downloads

1. Go to https://git-scm.com/downloads
2. Download for your operating system
3. Run the installer
4. **Verify installation**: Open terminal and type:
   ```bash
   git --version
   ```
   You should see a version number

### 6. Install Ollama (AI Model - Required for Voice Input)
**Download from**: https://ollama.ai/download

1. Go to https://ollama.ai/download
2. Click your operating system:
   - **Mac**: Download the .dmg file
   - **Windows**: Download the .exe file
   - **Linux**: Copy the installation command

3. **For Mac users:**
   - Run the downloaded .dmg file
   - Drag Ollama to Applications folder
   - Open Ollama from Applications

4. **For Windows users:**
   - Run the downloaded .exe file
   - Follow the installer instructions

5. **For Linux users:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

6. **Start Ollama and download the model:**
   ```bash
   ollama serve
   ```
   Then in a new terminal:
   ```bash
   ollama pull llama3
   ```

7. **Verify installation**: Open terminal and type:
   ```bash
   ollama --version
   ```
   You should see a version number

8. **Test the model**: 
   ```bash
   ollama run llama3 "Hello, how are you?"
   ```
   You should see a response from the AI model

## 🚀 Quick Start Guide

### Step 1: Open Terminal/Command Prompt
- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Windows**: Press `Windows + R`, type "cmd", press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 2: Navigate to the Project Folder
Copy and paste this command:
```bash
cd /Users/allansevilla/Desktop/Personal\ Projects/Lifesync
```

### Step 3: Install Frontend Dependencies
Copy and paste these commands:
```bash
cd life_sync_frontend
npm install
```

**What you should see:**
```
added 230 packages, and audited 230 packages in 430ms
35 packages are looking for funding
found 0 vulnerabilities
```

### Step 4: Install Backend Dependencies
Open a NEW terminal window and copy/paste:
```bash
cd /Users/allansevilla/Desktop/Personal\ Projects/Lifesync
cd lifesync_ai_backend
uv sync
```

**What you should see:**
```
✓ Resolved 15 packages in 0.1s
✓ Downloaded 15 packages in 0.5s
✓ Installed 15 packages in 0.2s
```

### Step 5: Start the Backend Server
In the backend terminal, copy and paste:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**What you should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal window open!** (Don't close it)

### Step 6: Start the Frontend Server
Open a NEW terminal window and copy/paste:
```bash
cd /Users/allansevilla/Desktop/Personal\ Projects/Lifesync
cd life_sync_frontend
npm run dev
```

**What you should see:**
```
> life_sync@0.0.0 dev
> vite
VITE v7.0.6  ready in 108 ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Keep this terminal window open too!** (Don't close it)

### Step 7: Open the App in Your Browser
1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: `http://localhost:5173`
3. You should see the LifeSync login page!

## 🎯 How to Use the App

### Creating an Account
1. Click "Sign up" on the login page
2. Fill in your details:
   - First Name: Your first name
   - Last Name: Your last name
   - Email: Your email address
   - Password: Choose a password
3. Click "Sign Up"
4. You'll be redirected to the login page

### Logging In
1. Enter your email and password
2. Click "Sign In"
3. You'll see the main app dashboard

### Using Voice Input
1. Click the "Voice" button (microphone icon)
2. Allow microphone access when prompted
3. Speak your task: "I need to buy groceries tomorrow"
4. Click "Create Tasks"
5. Your task will appear in the task list!

### Creating Tasks Manually
1. Click the "New" button
2. Fill in the task details
3. Click "Save"

## 🧪 Running Tests (Optional)

If you want to test that everything is working:

### Step 1: Install Test Dependencies
Open a THIRD terminal window and copy/paste:
```bash
cd /Users/allansevilla/Desktop/Personal\ Projects/Lifesync
pip install requests
```

### Step 2: Run the Tests
```bash
python test_lifesync_app.py
```

**What you should see:**
```
🚀 LifeSync Application - Comprehensive Test Suite
🧪 Test 1: Backend Server Health Check
  ✅ Backend server is running and accessible
🧪 Test 2: Frontend Server Health Check
  ✅ Frontend server is running
...
✅ ALL TESTS PASSED!
```

## 🛠️ Troubleshooting

### "Command not found" Errors

**Problem**: You see `zsh: command not found: node` or similar
**Solution**: 
1. **Node.js not installed**: Go to https://nodejs.org/ and install it
2. **Python not installed**: Go to https://www.python.org/downloads/ and install it
3. **uv not installed**: Follow the uv installation steps above
4. **Wrong folder**: Make sure you're in the right folder:
   ```bash
   cd /Users/allansevilla/Desktop/Personal\ Projects/Lifesync/lifesync_ai_backend
   ```

### "Port already in use" Errors
**Problem**: You see "Port 5173 is in use" or "Port 8000 is in use"
**Solution**: 
1. Close all terminal windows
2. Start over from Step 1
3. Or use different ports:
   - Backend: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`
   - Frontend will automatically find a free port

### "Cannot connect" Errors
**Problem**: Browser shows "Cannot connect to localhost"
**Solution**:
1. Make sure both terminal windows are still running
2. Check that you see the success messages in both terminals
3. Try refreshing the browser page
4. Make sure you're going to `http://localhost:5173` (not https)

### "Database connection" Errors
**Problem**: You see database connection errors
**Solution**:
1. Make sure PostgreSQL is installed and running
2. **Mac users**: `brew services start postgresql`
3. **Windows users**: Check if PostgreSQL service is running
4. The app will create the database automatically

### "Microphone not working" Errors
**Problem**: Voice input doesn't work
**Solution**:
1. Make sure you're using Chrome or Firefox
2. Allow microphone access when prompted
3. Check that your microphone is working in other apps
4. Try refreshing the page

### "AI model not working" Errors
**Problem**: Voice input creates tasks but they're not processed by AI
**Solution**:
1. Make sure Ollama is installed and running:
   ```bash
   ollama serve
   ```
2. Check if the model is downloaded:
   ```bash
   ollama list
   ```
3. If no models listed, download the model:
   ```bash
   ollama pull llama2
   ```
4. Test the model works:
   ```bash
   ollama run llama2 "Test message"
   ```
5. Make sure Ollama is running before starting the backend server

### "Permission denied" Errors
**Problem**: You see permission errors when installing
**Solution**:
1. **Mac/Linux**: Add `sudo` before commands:
   ```bash
   sudo npm install
   ```
2. **Windows**: Run Command Prompt as Administrator

## 📱 What You Can Do

### ✅ Features Available
- **Create an account** and log in
- **Add tasks** manually with title, description, priority
- **Use voice input** to create tasks by speaking
- **View all your tasks** in a list
- **Edit tasks** by clicking the menu (three dots)
- **Delete tasks** you don't need
- **Set due dates** for your tasks
- **Add priorities** (1-5, where 5 is most important)

### 🎤 Voice Input Examples
Try saying these:
- "I need to buy groceries tomorrow"
- "Call the doctor on Friday"
- "30 minute workout this afternoon"
- "Finish the report by next week"
- "Don't forget about the dentist appointment"

## 🔧 Stopping the App

When you're done:
1. Go to each terminal window
2. Press `Ctrl + C` (or `Cmd + C` on Mac)
3. Type `y` and press Enter if asked
4. Close the terminal windows

## 📞 Need Help?

If something doesn't work:
1. **Check all terminal windows** are still running
2. **Refresh your browser** page
3. **Try the troubleshooting steps** above
4. **Make sure you're in the right folders** when running commands
5. **Verify all software is installed** using the version commands above

## 🎓 For Class Project

This app demonstrates:
- ✅ **Full-stack development** (Frontend + Backend)
- ✅ **Modern web technologies** (React, FastAPI, Python)
- ✅ **AI integration** (Voice input with conversation analysis)
- ✅ **User authentication** (Secure login system)
- ✅ **Database integration** (Task storage and retrieval)
- ✅ **Professional testing** (Comprehensive test suite)
- ✅ **Real-world features** (Task management, voice input)

Perfect for showing off your programming skills! 🚀

## 🔗 Useful Links

- **Node.js**: https://nodejs.org/
- **Python**: https://www.python.org/downloads/
- **uv**: https://docs.astral.sh/uv/getting-started/installation/
- **PostgreSQL**: https://www.postgresql.org/download/
- **Git**: https://git-scm.com/downloads
- **Ollama**: https://ollama.ai/download
- **Chrome**: https://www.google.com/chrome/
- **Firefox**: https://www.mozilla.org/firefox/