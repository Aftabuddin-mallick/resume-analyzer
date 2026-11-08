# AI Resume Analyzer and Job Matcher

Upload a resume (PDF), paste a job description, and get a match score, missing skills, and AI-written suggestions. Rank saved jobs by how well they fit your resume, and review past analyses on the History page.

**Stack:** React + Vite + Tailwind CSS, FastAPI, SQLAlchemy (SQLite or PostgreSQL), pypdf, scikit-learn (TF-IDF cosine similarity), Google Gemini API.

## How scoring works
- Skills are extracted from the resume and job text using a dictionary of ~170 skills and aliases (`backend/skills.py`).
- Final score = 60% skill coverage + 40% TF-IDF cosine similarity.
- Gemini returns structured JSON feedback (summary, strengths, gaps, suggestions, rewritten bullets, keywords). If no API key is set or the call fails, rule-based tips are shown instead, so the app never breaks.

## Run locally
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your GEMINI_API_KEY (free: https://aistudio.google.com/apikey)
uvicorn main:app --reload   # http://localhost:8000/docs

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev                 # http://localhost:5173
```

## Deploy

### 1. Push to GitHub
```bash
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

### 2. Backend on Render
1. Render dashboard > New > **Blueprint** > pick your repo (it reads `render.yaml`). Or New > Web Service with Root Directory `backend`, Build `pip install -r requirements.txt`, Start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
2. Set environment variables: `GEMINI_API_KEY` (and optionally `DATABASE_URL`).
3. Copy the service URL, e.g. `https://resume-analyzer-api.onrender.com`.

Free Render services sleep after inactivity (first request can take ~1 minute) and SQLite data is wiped on each redeploy. For permanent history, create a free PostgreSQL database (Render or Neon) and set `DATABASE_URL` to its connection string.

### 3. Frontend on Vercel
1. Vercel > Add New Project > import the repo.
2. Set **Root Directory** to `frontend` (framework auto-detects as Vite).
3. Add environment variable `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy.

### 4. Lock down CORS (recommended)
In Render, set `CORS_ORIGINS` to your Vercel URL, e.g. `https://your-app.vercel.app`, then redeploy.

## Connect your Job Hunt data
Import many jobs at once with `POST /api/jobs/bulk`. Each item needs `title` and `description` (at least 30 characters); `company`, `location` and `url` are optional.

```bash
curl -X POST https://<render-url>/api/jobs/bulk -H "Content-Type: application/json" \
  -d '[{"title":"Data Analyst","company":"Acme","description":"SQL, Python, Tableau, and strong communication skills required."}]'
```

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/analyze` | multipart: `file`, `job_description`, `job_title` |
| GET | `/api/analyses` | history list |
| GET/DELETE | `/api/analyses/{id}` | one analysis |
| GET | `/api/analyses/{id}/rank-jobs` | jobs ranked for that resume |
| GET/POST | `/api/jobs` | list or add jobs |
| POST | `/api/jobs/bulk` | import many jobs |
| DELETE | `/api/jobs/{id}` | delete job |
| GET | `/api/health` | health check |
