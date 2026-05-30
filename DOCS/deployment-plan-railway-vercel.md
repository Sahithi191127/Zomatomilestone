# TastePilot — Railway + Vercel Deployment Plan

Deploy the **recommended** TastePilot stack in two parts:

| Host | Service | URL example |
|------|---------|-------------|
| **Vercel** | React SPA (`frontend/`) | `https://tastepilot.vercel.app` |
| **Railway** | FastAPI API (`src/app/api/`) | `https://tastepilot-api.up.railway.app` |

```
Browser → Vercel (static React)
              ↓ HTTPS /api/v1/*
         Railway (FastAPI + Parquet + Groq)
```

> **Not covered here:** Streamlit-only deploy → see [`deployementplan.md`](./deployementplan.md).

---

## What you are deploying

### Frontend (Vercel)

| Layer | Technology |
|--------|------------|
| UI | React 19 + TypeScript |
| Build | Vite 6 → static `frontend/dist/` |
| Dev proxy | `/api` and `/images` → localhost (production must use real API URL) |

### Backend (Railway)

| Layer | Technology |
|--------|------------|
| API | FastAPI + Uvicorn |
| Entry | `app.api.app:app` |
| Data | `data/processed/restaurants.parquet` (~5–6 MB) |
| AI | Groq (`LLM_API_KEY`) |
| Static | `/images` from repo `images/` |

Local reference:

```powershell
.\scripts\run_dev.ps1
# API: http://127.0.0.1:8000  |  UI: http://localhost:5173
```

---

## Prerequisites

1. **GitHub** — repo pushed (Vercel + Railway connect via GitHub).
2. **Vercel account** — [vercel.com](https://vercel.com)
3. **Railway account** — [railway.app](https://railway.app)
4. **Groq API key** — [console.groq.com](https://console.groq.com/) (recommended; fallback works without it)
5. **Restaurant data** — commit `data/processed/restaurants.parquet` (see [Data strategy](#data-strategy))

---

## Required code / config changes (before deploy)

The repo is set up for **local dev** (Vite proxy + localhost CORS). For production, apply these **once** before or during first deploy:

### 1. Frontend — API base URL

Vite’s dev proxy does **not** run on Vercel. Point the React app at the Railway API.

**A. Environment variable**

```bash
# Vercel project → Settings → Environment Variables
VITE_API_URL=https://YOUR-RAILWAY-APP.up.railway.app
```

**B. Update `frontend/src/api/client.ts`**

Use a shared base for all `fetch` calls, e.g.:

```typescript
const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

// fetch(apiUrl("/api/v1/health")) ...
```

**C. Logo / images**

`LOGO_SRC = "/images/..."` works in dev via proxy. In production, either:

- `VITE_API_URL + "/images/tastepilot-logo-dark.png"`, or  
- Host images on Vercel (`frontend/public/images/`) and keep `/images/...` relative to the SPA origin.

### 2. Backend — CORS

`src/app/api/app.py` currently allows only `localhost:5173`. Add your Vercel URL(s):

```python
# Prefer reading from env, e.g. CORS_ORIGINS=https://tastepilot.vercel.app,https://tastepilot-*.vercel.app
```

Set on Railway:

```bash
CORS_ORIGINS=https://tastepilot.vercel.app,https://your-preview-url.vercel.app
```

Include **preview** URLs if you use Vercel PR previews.

### 3. Backend — listen on `$PORT`

Railway assigns a dynamic port. Start command must use it:

```bash
uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
```

Do **not** use `reload=True` in production.

### 4. Backend — `PYTHONPATH`

Railway build/run must see `src` as the package root:

```bash
PYTHONPATH=src
```

### 5. Optional — slim production requirements

`requirements.txt` includes Streamlit; Railway can install everything, or you add `requirements-api.txt` without `streamlit` for faster builds.

---

## Data strategy

### Recommended — commit Parquet

1. Locally (once):

   ```powershell
   $env:PYTHONPATH = "src"
   python -m app.ingest
   ```

2. Commit `data/processed/restaurants.parquet` (~5–6 MB).

3. Railway deploy loads from `DATA_PATH` (resolved to repo root via `app.config.PROJECT_ROOT`).

### Not recommended on Railway free tier

- First-boot Hugging Face ingest (~574 MB) — slow, may OOM or timeout.

---

## Part 1 — Deploy API on Railway

### Step 1 — New project

1. Railway → **New Project** → **Deploy from GitHub repo**.
2. Select this repository.

### Step 2 — Service settings

| Setting | Value |
|---------|--------|
| **Root directory** | `/` (repo root) |
| **Builder** | Nixpacks (default) or Dockerfile |

### Step 3 — Start command

**Settings → Deploy → Start Command:**

```bash
uvicorn app.api.app:app --host 0.0.0.0 --port $PORT
```

**Settings → Variables:**

| Variable | Required | Example |
|----------|----------|---------|
| `PYTHONPATH` | Yes | `src` |
| `LLM_API_KEY` | Recommended | `gsk_...` |
| `DATA_PATH` | Optional | `data/processed/restaurants.parquet` |
| `CORS_ORIGINS` | Yes (after Vercel URL known) | `https://tastepilot.vercel.app` |
| `LLM_MODEL` | Optional | `llama-3.3-70b-versatile` |
| `BUDGET_LOW_MAX` | Optional | `500` |
| `BUDGET_MEDIUM_MAX` | Optional | `1500` |
| `MAX_CANDIDATES` | Optional | `30` |

### Step 4 — Optional `railway.toml` (repo root)

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.api.app:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 120
restartPolicyType = "on_failure"
```

### Step 5 — Optional `Procfile` (repo root)

```
web: uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
```

(Set `PYTHONPATH=src` in Railway variables, not in Procfile, unless your platform supports it.)

### Step 6 — Optional `Dockerfile` (more control)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data
COPY images ./images

ENV PYTHONPATH=src
ENV DATA_PATH=data/processed/restaurants.parquet

EXPOSE 8000
CMD uvicorn app.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
```

In Railway: **Settings → Builder → Dockerfile**.

### Step 7 — Verify API

After deploy, open:

```text
https://YOUR-SERVICE.up.railway.app/api/v1/health
```

Expected JSON:

```json
{ "status": "ok", "restaurants_loaded": 24711 }
```

If `restaurants_loaded` is `0`, fix `DATA_PATH` or commit Parquet.

Docs (optional): `https://YOUR-SERVICE.up.railway.app/docs`

---

## Part 2 — Deploy UI on Vercel

### Step 1 — New project

1. Vercel → **Add New** → **Project** → import GitHub repo.
2. **Root Directory:** `frontend`
3. **Framework Preset:** Vite

### Step 2 — Build settings

| Setting | Value |
|---------|--------|
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

### Step 3 — Environment variables

| Name | Value | Environments |
|------|--------|----------------|
| `VITE_API_URL` | `https://YOUR-SERVICE.up.railway.app` | Production, Preview, Development |

No trailing slash. Redeploy after changing.

### Step 4 — Optional `frontend/vercel.json`

SPA fallback + security headers:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [{ "key": "X-Content-Type-Options", "value": "nosniff" }]
    }
  ]
}
```

API calls go to `VITE_API_URL` (full URL), not Vercel rewrites — unless you add a reverse proxy rewrite (advanced).

### Step 5 — Update Railway CORS

After Vercel gives you a URL, add it to Railway `CORS_ORIGINS` and redeploy the API.

### Step 6 — Verify UI

1. Open `https://your-app.vercel.app`
2. Form loads areas/cuisines (metadata from Railway).
3. Submit search → loading → results or empty state.
4. Logo loads (check Network tab for `/images/...` or full API URL).

---

## Environment variable reference

### Railway (backend)

| Key | Purpose |
|-----|---------|
| `PYTHONPATH` | `src` — import `app.*` |
| `PORT` | Set by Railway (do not hardcode) |
| `LLM_API_KEY` | Groq secret |
| `DATA_PATH` | Parquet path (default under repo root) |
| `CORS_ORIGINS` | Comma-separated Vercel origins |
| `LLM_MODEL` | Groq model id |
| `BUDGET_LOW_MAX` / `BUDGET_MEDIUM_MAX` | Price bands |
| `MAX_CANDIDATES` | LLM candidate cap |

### Vercel (frontend)

| Key | Purpose |
|-----|---------|
| `VITE_API_URL` | Railway API origin (build-time) |

Never put `LLM_API_KEY` on Vercel — it must stay on Railway only.

---

## Deployment order

1. Commit Parquet + any code changes (API base URL, CORS, `$PORT`).
2. **Deploy Railway** → note public URL.
3. Set `VITE_API_URL` on Vercel → **deploy Vercel**.
4. Set `CORS_ORIGINS` on Railway with Vercel URL → **redeploy Railway**.
5. Smoke-test production.

---

## Repository layout (deploy-relevant)

```text
ZOMATOMILESTONE/
├── requirements.txt          # Railway pip install
├── runtime.txt               # Optional Python pin (Streamlit/Railway)
├── railway.toml              # Optional Railway config
├── Dockerfile                  # Optional Railway Docker build
├── data/processed/
│   └── restaurants.parquet   # Commit for fast API boot
├── images/                   # API serves /images/*
├── src/
│   └── app/
│       ├── api/
│       │   ├── app.py        # FastAPI + CORS
│       │   └── routes.py     # /api/v1/*
│       └── config.py         # PROJECT_ROOT, DATA_PATH
└── frontend/
    ├── package.json
    ├── vite.config.ts        # Dev proxy only
    ├── vercel.json           # Optional
    └── src/api/client.ts     # Needs VITE_API_URL in prod
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| CORS error in browser | Vercel origin not in `CORS_ORIGINS` | Add exact URL; redeploy API |
| `Failed to fetch` / 404 on API | Wrong `VITE_API_URL` or not rebuilt | Fix env; redeploy Vercel |
| `restaurants_loaded: 0` | Missing Parquet on Railway | Commit file or fix `DATA_PATH` |
| 502 / crash on Railway | OOM, bad start command | Check logs; use `--port $PORT`, no reload |
| Logo broken | Relative `/images` hits Vercel | Prefix with `VITE_API_URL` or use `public/` |
| AI always fallback | Missing `LLM_API_KEY` on Railway | Add secret; redeploy |
| Preview deploy broken | Preview URL not in CORS | Add `https://*-*.vercel.app` pattern or each preview URL |
| Slow cold start | Free tier sleep | Upgrade or accept first-hit delay |

**Logs**

- Railway: Project → Service → **Deployments** → **View logs**
- Vercel: Project → **Deployments** → build/runtime logs

---

## Security

- Keep `LLM_API_KEY` only on Railway.
- Do not commit `.env`.
- Restrict `CORS_ORIGINS` to your Vercel domains (avoid `*` in production).
- Rotate Groq keys if exposed.
- Consider Railway/Vercel team access and branch protection on `main`.

---

## Cost & limits (typical hobby tier)

| Platform | Notes |
|----------|--------|
| **Vercel** | Generous static hosting; bandwidth limits on free tier |
| **Railway** | Usage-based credits; Parquet + pandas needs ~512MB–1GB RAM recommended |
| **Groq** | Separate API usage limits |

---

## Alternatives

| Approach | When |
|----------|------|
| **Render** instead of Railway | Same FastAPI deploy; use `PORT` + start command |
| **Netlify / Cloudflare Pages** instead of Vercel | Same static `dist`; set `VITE_API_URL` |
| **Single Railway service** | Build React into `dist/`, mount static in FastAPI — one URL, no CORS |
| **Streamlit Cloud** | Legacy UI only — see `deployementplan.md` |

---

## Quick reference

| Item | Value |
|------|--------|
| Frontend host | Vercel (`frontend/`) |
| Backend host | Railway (repo root, `PYTHONPATH=src`) |
| API health | `GET /api/v1/health` |
| Vercel env | `VITE_API_URL` |
| Railway env | `LLM_API_KEY`, `CORS_ORIGINS`, `PYTHONPATH=src` |
| Data | `data/processed/restaurants.parquet` |
| Local dev | `.\scripts\run_dev.ps1` |

---

## Checklist (copy before go-live)

- [ ] `restaurants.parquet` committed
- [ ] `frontend/src/api/client.ts` uses `VITE_API_URL`
- [ ] `VITE_API_URL` set on Vercel
- [ ] Railway start command uses `$PORT` and `PYTHONPATH=src`
- [ ] `LLM_API_KEY` set on Railway
- [ ] `CORS_ORIGINS` includes production (and preview) Vercel URLs
- [ ] Health check returns `restaurants_loaded > 0`
- [ ] End-to-end search works on production URL
