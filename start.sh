#!/bin/bash
echo "Starting Chunav Mitra..."

# Start backend
cd vote
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    python -m venv venv
    source venv/Scripts/activate
fi
pip install -r requirements.txt -q
python main.py &
BACKEND_PID=$!
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Start frontend
cd ../chunav-shadi-assistant-main
npm install -q
npm run dev &
FRONTEND_PID=$!
echo "Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"

echo ""
echo "Chunav Mitra is live!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

wait $BACKEND_PID $FRONTEND_PID
