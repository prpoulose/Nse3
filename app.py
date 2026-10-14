import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "PRIME FLOW Backend"

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    description="Secure starter API for the PRIME FLOW NSE F&O dashboard. Live market data is not connected yet.",
)

# Restrict browser access to the GitHub Pages dashboard by default.
# Set ALLOWED_ORIGINS in Render if your frontend URL changes.
_origins = os.getenv("ALLOWED_ORIGINS", "https://prpoulose.github.io").strip()
allowed_origins = [origin.strip() for origin in _origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "status": "running",
        "market_data": "NOT_CONNECTED",
        "message": "Backend starter is running. No live prices or scan signals are generated yet.",
        "utc_time": utc_now(),
    }


@app.get("/health")
def health():
    return {"ok": True, "service": APP_NAME, "utc_time": utc_now()}


@app.get("/api/status")
def api_status():
    # Deliberately do not return credential values or secret-presence details.
    return {
        "service": APP_NAME,
        "backend": "ONLINE",
        "market_data": "NOT_CONNECTED",
        "scanner": "NOT_IMPLEMENTED",
        "order_placement": "DISABLED",
        "updated_at_utc": utc_now(),
        "parameters": {
            "01_open_interest": "NOT_CONNECTED",
            "02_volume_vs_5d_average": "NOT_CONNECTED",
            "03_todays_price_movement": "NOT_CONNECTED",
            "04_5d_price_and_delivery": "NOT_CONNECTED",
            "05_10d_support_resistance": "NOT_CONNECTED",
            "06_news_and_effect": "NOT_CONNECTED",
            "07_overall_conclusion": "NOT_CONNECTED",
            "08_buyer_seller_footprint": "NOT_CONNECTED",
            "09_high_volume_signal": "NOT_CONNECTED",
            "10_ema_and_rsi": "NOT_CONNECTED",
            "11_data_status": "ONLINE_BACKEND_ONLY",
            "12_global_market_and_events": "NOT_CONNECTED",
        },
    }


@app.post("/api/scan")
def scan():
    # Do not fabricate stock data or signals before a verified market-data adapter exists.
    raise HTTPException(
        status_code=503,
        detail=(
            "Scanner is not ready: live market-data integration has not been configured. "
            "No symbols were scanned and no trade signals were generated."
        ),
    )
