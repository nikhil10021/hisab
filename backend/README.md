# HISAB Backend

The backend is a stateless FastAPI service. No real calculator is enabled in this
skeleton; plugins are exposed only when their `is_live` flag is true.

## Setup

Use Python 3.12 or newer and create a virtual environment from this directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Configure `ENVIRONMENT` and `CORS_ORIGINS` in `.env` for local or deployed use.
Do not commit `.env` or put secrets in `VITE_` variables.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

The API is under `/api/v1`. Interactive API documentation is available in
development and disabled when `ENVIRONMENT=prod`.

## Test and lint

```powershell
python -m pytest
python -m ruff check app tests
python -m ruff format --check app tests
python -m mypy --strict
```
