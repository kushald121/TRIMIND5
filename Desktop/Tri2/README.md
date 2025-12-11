# LLM Council - Setup Guide

## Prerequisites

- Python 3.10 or higher
- Node.js and npm
- An OpenRouter API key (get one from https://openrouter.ai/keys)

## Environment Setup

Create a `.env` file in the root directory with your OpenRouter API key:

```
OPENROUTER_API_KEY=your_api_key_here
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install fastapi uvicorn[standard] python-dotenv httpx pydantic
```

### 4. Install Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd TriMind
npm install
```

## Running the Application

### Option 1: Manual Start

1. Start the backend server:
   ```bash
   # From the root directory
   python -m backend.main
   ```
   The backend will be available at `http://localhost:8002`

2. Start the frontend:
   ```bash
   # From the TriMind directory
   npm run dev
   ```
   The frontend will be available at `http://localhost:5174`

### Option 2: Using the Startup Script

On Windows, you can simply double-click the `start.bat` file, or run it from the command line:

```bash
start.bat
```

This will automatically start both the backend and frontend servers.

## API Endpoints

The backend provides the following API endpoints:

- `GET /` - Health check endpoint
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations/{conversation_id}` - Get a specific conversation
- `POST /api/conversations/{conversation_id}/message` - Send a message (non-streaming)
- `POST /api/conversations/{conversation_id}/message/stream` - Send a message (streaming)

## Architecture

The application consists of:

1. **Frontend** (React + TypeScript + Vite):
   - Provides the user interface for interacting with the LLM Council
   - Displays real-time responses from individual agents
   - Shows the final synthesized answer

2. **Backend** (FastAPI):
   - Implements a 3-stage council process:
     - Stage 1: Collect responses from multiple LLMs
     - Stage 2: Rank responses using a referee LLM
     - Stage 3: Synthesize a final answer based on rankings
   - Streams responses in real-time using Server-Sent Events (SSE)

## Troubleshooting

### Port Conflicts

If you encounter port conflicts, you can change the backend port in `backend/main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Change this port number
```

Make sure to update the frontend API URL in `TriMind/src/lib/api.ts` to match:

```typescript
const API_BASE_URL = 'http://localhost:8002';  // Change this port number
```

And update the frontend port in `TriMind/vite.config.ts`:

```typescript
server: {
  port: 5174,  // Change this port number
}
```

### Virtual Environment Issues

If you have trouble activating the virtual environment, make sure you're using the correct activation script for your operating system.

### Dependency Installation Issues

If you encounter issues installing dependencies, try upgrading pip first:

```bash
python -m pip install --upgrade pip
```