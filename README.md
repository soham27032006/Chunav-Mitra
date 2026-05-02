# 🗳️ Chunav Mitra — AI Election Assistant

> **Google Virtual Prompt Wars 2026** | Making democracy accessible through Desi Wedding analogies!

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-orange)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎊 "Desh ki Sabse Badi Shaadi ke Guest Hain Aap!"

Chunav Mitra explains the entire Indian election process using
**Desi Wedding (Shaadi) analogies** — making democracy fun and relatable!

| Election Term | Shaadi Analogy |
|---------------|---------------|
| Voter List | Guest List (Mehman List) |
| Polling Booth | Mandap |
| Indelible Ink | Mehndi |
| Manifesto | Shagun ka Menu |
| Voting | Shagun Dena |
| EVM Machine | Mangalsutra Moment |
| Candidate | Dulha/Dulhan |
| Election Commission | Wedding Planner |

## ✨ Features

- 🤖 **AI Chat** — Hindi + English, voice input, streaming responses
- 🎫 **Voter Check** — Verify if you're on the electoral roll
- 🏛️ **Booth Finder** — Find nearest polling booth via GPS/pincode
- 📖 **Election Dictionary** — Explain any term with shaadi analogy
- 📅 **Election Timeline** — All phases with countdown
- 📊 **Live Stats** — Real-time usage dashboard

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI | Google Gemini API |
| Translation | deep-translator (FREE) |
| Maps | Leaflet.js + OpenStreetMap (FREE) |
| Database | Firebase Firestore |
| Backend | FastAPI + Python 3.11 |
| Frontend | React 19 + TypeScript + TailwindCSS |
| Animations | Framer Motion |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd vote
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python main.py
# → http://localhost:8000
```

### Frontend Setup
```bash
cd chunav-shadi-assistant-main
npm install
cp .env.example .env
# Add VITE_API_BASE_URL=http://localhost:8000
npm run dev
# → http://localhost:5173
```

### One Command Start
```bash
bash start.sh
```

## 🔑 API Keys Required

| Key | Source | Free? |
|-----|--------|-------|
| GEMINI_API_KEY | aistudio.google.com | ✅ Yes |
| FIREBASE_PROJECT_ID | console.firebase.google.com | ✅ Yes |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/ask | AI chat with Gemini |
| GET | /api/ask/stream | SSE streaming |
| POST | /api/check-voter | Voter roll lookup |
| POST | /api/find-booth | Nearest booth |
| GET | /api/timeline | Election phases |
| POST | /api/explain | Term explainer |
| GET | /api/stats | Live stats |

## 🏆 Google Prompt Wars 2026

Built for the Google Virtual Prompt Wars 2026 competition.
Evaluation criteria: Code Quality, Security, Testing, 
Accessibility, Efficiency.

## 🇮🇳 Problem Statement Alignment

This project directly addresses the challenge of making 
election information accessible to ALL Indian citizens:

- 970M+ voters across 28 states and 8 UTs
- 22 official languages supported via translation
- First-time voter education through relatable analogies
- Real-time voter registration and booth lookup
- Powered entirely by Google AI + Firebase ecosystem

Official Resources:
- Voter search: [electoralsearch.eci.gov.in](https://electoralsearch.eci.gov.in)
- Registration: [nvsp.in](https://nvsp.in)
- Helpline: 1950

## 📄 License

MIT License — see LICENSE file.

## 🙏 Made with ❤️ for Indian Democracy

*"Har vote ek shagun hai — desh ke liye sabse bada tohfa!"*
