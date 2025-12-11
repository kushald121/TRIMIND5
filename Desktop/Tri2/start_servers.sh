#!/bin/bash

echo "Starting LLM Council Servers..."
echo ""

# Start backend
echo "Starting backend on http://localhost:8002..."
cd "$(dirname "$0")"
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
python -m backend.main &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:5174..."
cd TriMind
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✓ Servers started!"
echo "  Backend:  http://localhost:8002 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:5174 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait

