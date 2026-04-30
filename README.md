# Chunav Mitra — Election Assistant API

## Setup (5 minutes)

```bash
# 1. Clone & enter
cd election-assistant

# 2. Create virtual env
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install deps
pip install -r requirements.txt

# 4. Setup env
cp .env.example .env
# Fill in your API keys in .env

# 5. Add Firebase service account JSON
# Download from Firebase Console → Project Settings → Service Accounts
# Save as: firebase-service-account.json

# 6. Run
python main.py
# API live at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Keys (all FREE)
| Key | Where to get |
|-----|-------------|
| GEMINI_API_KEY | aistudio.google.com |
| GOOGLE_MAPS_API_KEY | console.cloud.google.com → Maps JavaScript API |
| GOOGLE_TRANSLATE_API_KEY | console.cloud.google.com → Cloud Translation API |
| Firebase | console.firebase.google.com → Project Settings |

## Endpoints
- POST /api/ask — Main chat with Gemini + shaadi analogies
- POST /api/check-voter — Voter roll lookup
- POST /api/find-booth — Nearest booth via Google Maps
- GET  /api/timeline — Election phases and deadlines
