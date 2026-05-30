# TastePilot — Deploy Backend on Railway + Frontend on Vercel

Step-by-step guide to deploy **TastePilot** as a split stack:

| Platform | Role | What runs |
|----------|------|-----------|
| **[Railway](https://railway.app)** | **Backend** | FastAPI API, Parquet data, Groq LLM, `/images` static |
| **[Vercel](https://vercel.com)** | **Frontend** | React + Vite SPA (`frontend/`) |

**GitHub repo:** [github.com/Sahithi191127/Zomatomilestone](https://github.com/Sahithi191127/Zomatomilestone)

```
User browser
    │
    ▼
https://your-app.vercel.app          (Vercel — React UI)
    │
    │  HTTPS  VITE_API_URL + /api/v1/*
    ▼
https://your-api.up.railway.app      (Railway — FastAPI)
    │
    ├── restaurants.parquet
    ├── Groq API (LLM_API_KEY)
    └── images/ (logo, loading ring, etc.)
```

> **Streamlit UI** (`src/app/main.py`) is **not** used in this deploy path. Use Railway + Vercel for the React app only.

---

## Architecture summary

### Backend (Railway)

| Item | Detail |
|------|--------|
| Framework | FastAPI + Uvicorn |
| App module | `app.api.app:app` |
| Routes | `/api/v1/health`, `/api/v1/metadata/*`, `/api/v1/recommendations` |
| Config | `railway.toml`, `requirements-api.txt`, `Procfile` |
| Data | `data/processed/restaurants.parquet` (committed in repo) |
| Secrets | `LLM_API_KEY`, `CORS_ORIGINS` (Railway variables only) |

### Frontend (Vercel)

| Item | Detail |
|------|--------|
| Framework | React 19 + TypeScript + Vite 6 |
| Root directory | `frontend/` |
| Build output | `frontend/dist/` |
| API wiring | `VITE_API_URL` → `frontend/src/api/config.ts` |
| SPA routing | `frontend/vercel.json` |

### Local dev (unchanged)

```powershell
.\scripts\run_dev.ps1
# UI:  http://localhost:5173
# API: http://127.0.0.1:8000
```

Leave `VITE_API_URL` empty locally — Vite proxies `/api` and `/images` to port 8000.

---

## Prerequisites

1. Code on GitHub: [Sahithi191127/Zomatomilestone](https://github.com/Sahithi191127/Zomatomilestone) (includes `restaurants.parquet`).
2. [Railway](https://railway.app) account (GitHub login).
3. [Vercel](https://vercel.com) account (GitHub login).
4. [Groq API key](https://console.groq.com/) — recommended for AI rankings (fallback works without it).

---

## Already configured in this repo

You do **not** need extra code changes before deploy. The repo includes:

| Feature | File(s) |
|---------|---------|
| API base URL for production | `frontend/src/api/config.ts`, `frontend/src/api/client.ts` |
| Assets (logo, ring) | `assetUrl()` + `frontend/public/images/` fallback on Vercel |
| CORS + Vercel previews | `CORS_ORIGINS` env + `https://*.vercel.app` regex |
| Railway port + no hot reload | `src/app/api/main.py`, `railway.toml` |
| Slim API dependencies | `requirements-api.txt` |
| Optional Docker build | `Dockerfile` |
| Vercel SPA config | `frontend/vercel.json`, Node ≥ 18 in `package.json` |
| Missing `VITE_API_URL` warning | `vite.config.ts` build warn, `App.tsx` alert |
| API root metadata | `GET /` on Railway |
| Env templates | `.env.example`, `frontend/.env.example` |

---

## Deployment order (follow this sequence)

1. **Deploy Railway (backend)** → copy public API URL  
2. **Deploy Vercel (frontend)** → set `VITE_API_URL` to Railway URL  
3. **Update Railway `CORS_ORIGINS`** with your Vercel URL → redeploy API  
4. **Smoke-test** production  

---

# Part 1 — Backend on Railway

## 1. Create the Railway project

1. Go to [railway.app](https://railway.app) → **New Project**.
2. **Deploy from GitHub repo** → select **Zomatomilestone**.
3. Railway creates a service from the repo root.

## 2. Confirm Railway reads `railway.toml`

The repo root contains:

```toml
# railway.toml (already in repo)
[env]
PYTHONPATH = "src"

[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements-api.txt"

[deploy]
startCommand = "sh -c 'uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}'"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 120
restartPolicyType = "on_failure"
```

If the dashboard overrides this, align manually:

| Setting | Value |
|---------|--------|
| **Root directory** | `/` (repository root) |
| **Start command** | `sh -c 'uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}'` (shell required so `$PORT` expands) |
| **Build** | `pip install -r requirements-api.txt` |

## 3. Set Railway environment variables

**Service → Variables** (or **Shared Variables**):

| Variable | Required | Value |
|----------|----------|--------|
| `PYTHONPATH` | Yes* | `src` (*also set in `railway.toml`*) |
| `LLM_API_KEY` | Recommended | Your Groq key (`gsk_...`) |
| `CORS_ORIGINS` | After Vercel deploy | `https://YOUR-APP.vercel.app` (comma-separated for previews) |
| `DATA_PATH` | Optional | `data/processed/restaurants.parquet` (default) |
| `LLM_MODEL` | Optional | `llama-3.3-70b-versatile` |

**Do not** set `PORT` — Railway injects it automatically.

Example `CORS_ORIGINS` once Vercel is live:

```bash
CORS_ORIGINS=https://zomatomilestone.vercel.app,https://zomatomilestone-git-main-sahithi191127.vercel.app
```

Use your **exact** Vercel production and preview URLs from the Vercel dashboard.

## 4. Generate a public domain

1. Railway service → **Settings** → **Networking** → **Generate domain**.
2. Copy the URL, e.g. `https://zomatomilestone-production.up.railway.app`.
3. Save this — you need it for `VITE_API_URL` on Vercel.

## 5. Verify the backend

Open in a browser or curl:

```text
https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/v1/health
```

Expected:

```json
{
  "status": "ok",
  "restaurants_loaded": 24711
}
```

| Result | Action |
|--------|--------|
| `restaurants_loaded: 0` | Parquet missing on deploy — confirm `data/processed/restaurants.parquet` is in GitHub |
| 502 / crash | Open **Deployments → Logs**; check `PYTHONPATH=src` and start command |
| 404 on `/health` | Use `/api/v1/health` (not `/health`) |

Optional API docs: `https://YOUR-RAILWAY-DOMAIN/docs`

---

# Part 2 — Frontend on Vercel

## 1. Import the GitHub project

1. [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. Import **Sahithi191127/Zomatomilestone**.

## 2. Configure the project (critical)

| Setting | Value |
|---------|--------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

## 3. Set environment variables

**Settings → Environment Variables:**

| Name | Value | Environments |
|------|--------|----------------|
| `VITE_API_URL` | `https://YOUR-RAILWAY-DOMAIN.up.railway.app` | Production, Preview, Development |

Rules:

- **No trailing slash** on the Railway URL.
- **Redeploy** after changing `VITE_API_URL` (it is baked in at build time).

Example:

```bash
VITE_API_URL=https://zomatomilestone-production.up.railway.app
```

## 4. Deploy

Click **Deploy**. Vercel runs `npm run build` in `frontend/` and hosts `dist/`.

Your app URL will look like:

```text
https://zomatomilestone.vercel.app
```

(or a similar `*.vercel.app` subdomain)

## 5. Connect CORS on Railway

1. Copy your **production** Vercel URL from the Vercel dashboard.
2. Railway → **Variables** → set `CORS_ORIGINS` to that URL (add preview URLs if needed).
3. **Redeploy** the Railway service.

## 6. Verify the frontend

1. Open your Vercel URL.
2. Home form loads **areas** and **cuisines** (calls Railway metadata).
3. Submit preferences → loading → results or empty state.
4. DevTools → Network: API requests go to `https://YOUR-RAILWAY-DOMAIN.../api/v1/...`
5. Logo/images load from `https://YOUR-RAILWAY-DOMAIN.../images/...`

---

## Environment variables (complete reference)

### Railway — backend only

| Key | Purpose |
|-----|---------|
| `PYTHONPATH` | `src` — Python imports `app.*` |
| `PORT` | Injected by Railway — do not set manually |
| `LLM_API_KEY` | Groq API key (server-side secret) |
| `CORS_ORIGINS` | Comma-separated frontend origins (Vercel URLs) |
| `DATA_PATH` | Parquet file path (default: `data/processed/restaurants.parquet`) |
| `LLM_MODEL` | Groq model id |
| `BUDGET_LOW_MAX` / `BUDGET_MEDIUM_MAX` | Price band thresholds |
| `MAX_CANDIDATES` | Max restaurants sent to LLM |

### Vercel — frontend only

| Key | Purpose |
|-----|---------|
| `VITE_API_URL` | Railway API origin (required in production) |

**Never** put `LLM_API_KEY` on Vercel.

---

## Repository layout (deploy-relevant)

```text
Zomatomilestone/                    ← Railway deploys from here
├── railway.toml                    ← Railway config (committed)
├── requirements-api.txt            ← Railway pip install
├── Procfile                        ← Alternate start command
├── runtime.txt                     ← Python 3.11 pin
├── data/processed/
│   └── restaurants.parquet         ← Required for API
├── images/                         ← Served at /images/*
└── src/app/api/                    ← FastAPI app

frontend/                           ← Vercel root directory
├── package.json
├── vercel.json
├── .env.example                    ← VITE_API_URL template
└── src/api/
    ├── config.ts                   ← API_BASE, apiUrl(), assetUrl()
    └── client.ts                   ← fetch wrappers
```

---

## Troubleshooting

| Symptom | Platform | Fix |
|---------|----------|-----|
| CORS error in browser console | Both | Add exact Vercel URL to Railway `CORS_ORIGINS`; redeploy API |
| `Failed to fetch` / network error | Vercel | Wrong `VITE_API_URL`; rebuild after fixing |
| API calls go to `localhost` | Vercel | `VITE_API_URL` not set for Production; redeploy |
| `restaurants_loaded: 0` | Railway | Parquet not in repo or wrong `DATA_PATH` |
| 502 / service crash | Railway | Check logs; memory ≥ 512MB; confirm `$PORT` in start command |
| Logo / images 404 | Vercel | Should load from Railway (`assetUrl`); verify `VITE_API_URL` |
| AI always uses fallback | Railway | Set `LLM_API_KEY`; redeploy |
| Preview deploy CORS fails | Railway | Add preview URL to `CORS_ORIGINS` |
| Build fails on Vercel | Vercel | Root directory must be `frontend`; Node 18+ |
| `ModuleNotFoundError: app` | Railway | `PYTHONPATH=src` |

**Logs**

- Railway: Service → **Deployments** → **View logs**
- Vercel: Project → **Deployments** → build log

---

## Security checklist

- [ ] `.env` is **not** committed (in `.gitignore`)
- [ ] `LLM_API_KEY` only on Railway
- [ ] `CORS_ORIGINS` lists only your Vercel domains (not `*`)
- [ ] Groq key rotated if ever exposed

---

## Cost notes (hobby / student tier)

| Platform | Typical use |
|----------|-------------|
| **Vercel** | Static hosting; free tier for personal projects |
| **Railway** | Usage-based credits; recommend ≥ 512MB RAM for pandas + Parquet |
| **Groq** | Separate API quota |

---

## Go-live checklist

### Railway (backend)

- [ ] GitHub repo connected
- [ ] Deploy succeeded; health URL returns `restaurants_loaded > 0`
- [ ] Public domain generated
- [ ] `LLM_API_KEY` set
- [ ] `CORS_ORIGINS` includes Vercel production URL

### Vercel (frontend)

- [ ] Root directory = `frontend`
- [ ] `VITE_API_URL` = Railway public URL (no trailing slash)
- [ ] Production deploy succeeded
- [ ] Form loads metadata; search returns results

### End-to-end

- [ ] No CORS errors in browser DevTools
- [ ] API requests hit `*.railway.app`
- [ ] Images load from Railway `/images/`

---

## Quick reference

| Question | Answer |
|----------|--------|
| Where is the backend? | **Railway** — repo root, FastAPI |
| Where is the frontend? | **Vercel** — `frontend/` directory |
| GitHub repo | https://github.com/Sahithi191127/Zomatomilestone |
| API health check | `GET /api/v1/health` on Railway URL |
| Vercel env | `VITE_API_URL` |
| Railway env | `LLM_API_KEY`, `CORS_ORIGINS`, `PYTHONPATH=src` |
| Deploy order | Railway → Vercel → CORS → test |

---

## Alternatives (not this guide)

| Option | Notes |
|--------|--------|
| **Render** instead of Railway | Same FastAPI setup; use `$PORT` + `PYTHONPATH=src` |
| **Netlify / Cloudflare Pages** instead of Vercel | Same `dist` build; set `VITE_API_URL` |
| **Single Railway service** | Serve React `dist` from FastAPI — one URL, no CORS |
| **Streamlit Cloud** | Legacy `src/app/main.py` UI — separate deploy path |
