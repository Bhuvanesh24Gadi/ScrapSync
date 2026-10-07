# ScrapSync — Hackathon MVP

ScrapSync is a software-only B2B resource exchange prototype. It creates a structured material passport, finds compatible buyers, explains the compatibility score, and tracks exchange requests and estimated circular impact.

## Stack
- React + Vite
- FastAPI + SQLAlchemy
- SQLite by default (zero database setup)
- Professional dark/mint UI

## Run
Open two terminals.

### Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

The backend seeds a demo network automatically. No PostgreSQL, Docker, API keys, or external AI service is required for the MVP.

## Demo flow
Overview → Load demo network → List material → Opportunity Radar → expand reasoning → Send exchange request → Impact.
