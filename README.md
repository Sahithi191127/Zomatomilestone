# Zomato AI Restaurant Recommendation

AI-powered restaurant recommendations using the [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) dataset.

## Prerequisites

- Python 3.11+
- Internet access for first-time Hugging Face download (~574 MB)

## Setup

```powershell
cd ZOMATOMILESTONE
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

## TastePilot UI (React + FastAPI) — recommended

**One command (API + Vite dev server):**

```powershell
.\scripts\run_dev.ps1
```

- **React app:** http://localhost:5173  
- **API:** http://127.0.0.1:8000 (docs at http://127.0.0.1:8000/docs)

**Or run separately:**

```powershell
# Terminal 1 — API
.\scripts\run_api.ps1

# Terminal 2 — frontend (first time: cd frontend && npm install)
cd frontend
npm run dev
```

The React app proxies `/api` and `/images` to the API. All recommendation logic stays in Python (`app.services`).

## Deploy Streamlit (Community Cloud)

See **[DOCS/deployementplan.md](DOCS/deployementplan.md)** for full steps.

- **Main file:** `src/app/main.py`
- **Secrets:** copy [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) → `.streamlit/secrets.toml` (local) or paste into Cloud dashboard
- **Data:** commit `data/processed/restaurants.parquet` before deploy (~5 MB)

## Deploy React + FastAPI (Vercel + Railway)

See **[DOCS/deployment-plan-railway-vercel.md](DOCS/deployment-plan-railway-vercel.md)** for full steps.

| Platform | What |
|----------|------|
| **Railway** | FastAPI (`railway.toml`, `requirements-api.txt`, `PYTHONPATH=src`) |
| **Vercel** | React app (`frontend/`, set `VITE_API_URL` to your Railway URL) |

After deploy, set Railway `CORS_ORIGINS` to your Vercel URL(s). Local dev needs no `VITE_API_URL` (Vite proxy).

## Phase 6: Streamlit UI (legacy)

**Easiest (from project root, with venv activated):**

```powershell
.\scripts\run_ui.ps1
```

Or manually:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run src/app/main.py
```

Then open **http://localhost:8501** in your browser if it does not open automatically.

**Do not** use `python src/app/main.py` alone — that runs Streamlit in "bare mode" with no web server. Either use `streamlit run` or `python src/app/main.py` (which now re-invokes Streamlit for you).

**Troubleshooting**

| Symptom | Fix |
|--------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run from project root; use `.\scripts\run_ui.ps1` or activate `.venv` first |
| Blank page / nothing loads | Wait ~10s on first load (Parquet cache); refresh the browser |
| Browser never opens | Go to http://localhost:8501 manually |
| Port in use | `streamlit run src/app/main.py --server.port 8502` |

Form fields map 1:1 with `UserPreferences` (location, budget, cuisine, min rating, additional preferences, top_k).

## Phase 5: Orchestrator (single entry point)

CLI smoke via orchestrator:

```powershell
$env:PYTHONPATH = "src"
python scripts/recommend_smoke.py --location Btm --budget medium --cuisine italian --min-rating 4.0 --top-k 5
```

## Phase 4: Groq recommendations

Requires `LLM_API_KEY` in `.env` (get one at https://console.groq.com/).
Without an API key, the engine uses rating-based fallback explanations.

## Phase 1: Data ingestion

Download, normalize, and cache restaurants to Parquet:

```powershell
$env:PYTHONPATH = "src"
python -m app.ingest
# or
python scripts/ingest.py
```

Force re-download from Hugging Face:

```powershell
python -m app.ingest --refresh
```

### Verify

```powershell
$env:PYTHONPATH = "src"
python -c "from app.config import settings; print(settings.data_path)"
python -c "from app.data.repository import RestaurantRepository; r=RestaurantRepository.from_cache(); print(len(r), r.get_cities()[:5])"
pytest
```

## Environment variables

See `.env.example` for `DATA_PATH`, `BUDGET_LOW_MAX`, `BUDGET_MEDIUM_MAX`, and LLM settings.
