# PRIME FLOW backend starter

This is a safe starter API for the PRIME FLOW NSE F&O dashboard. It does **not** connect to Angel One yet and does not return live prices, scan stocks, or place orders.

## Files
- `app.py` — FastAPI health/status API and a scan endpoint that intentionally reports “not ready”.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — Render Docker deployment definition.

## Add to the existing `prpoulose/Nse3` repository
Upload these three files (`app.py`, `requirements.txt`, and `Dockerfile`) to the repository root, alongside the existing `index.html`. Do not delete or replace the existing website files. `README.md` is optional and may be merged with the existing README rather than replacing it.

## Render configuration
- Service type: Web Service
- Runtime: Docker
- Branch: `main`
- Dockerfile Path: `./Dockerfile`
- Health check path (if requested): `/health`
- `ALLOWED_ORIGINS` (optional): `https://prpoulose.github.io`

Do not add Angel One credentials yet. Never put API keys, client PINs, passwords, or TOTP secrets in source code, HTML, a public GitHub repository, or screenshots. Credentials should be configured only as private Render environment variables after the starter service is verified.

## Endpoints
- `GET /health` — basic health check
- `GET /api/status` — shows backend status and the 12 planned data categories
- `POST /api/scan` — deliberately returns HTTP 503 until a verified live market-data integration and scanner are implemented

## Important
A running backend is not a live market scanner. Market-data endpoints, API permissions, licensing, request limits, and any static-IP requirements must be checked before implementing the Angel One integration. No order placement is included.
