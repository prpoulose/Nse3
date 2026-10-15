
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "PRIME FLOW Backend"

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    description="PRIME FLOW NSE F&O dashboard backend",
)

_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://prpoulose.github.io",
).strip()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in _origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "status": "running",
        "market_data": "NOT_CONNECTED",
        "utc_time": utc_now(),
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": APP_NAME,
        "utc_time": utc_now(),
    }


@app.get("/api/status")
def api_status():
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
    raise HTTPException(
        status_code=503,
        detail=(
            "Scanner is not ready. Live market data is not connected. "
            "No symbols were scanned and no trade signals were generated."
        ),
    )


@app.get("/api/angel/status")
def angel_status():
    required = [
        "ANGEL_API_KEY",
        "ANGEL_CLIENT_ID",
        "ANGEL_MPIN",
        "ANGEL_TOTP_SECRET",
    ]

    missing = [
        name for name in required
        if not os.getenv(name)
    ]

    return {
        "service": APP_NAME,
        "angel_environment": (
            "MISSING_SETTINGS" if missing
            else "SETTINGS_PRESENT"
        ),
        "missing_settings": missing,
        "authentication_test": "NOT_RUN",
        "market_data": "NOT_CONNECTED",
        "order_placement": "DISABLED",
    }
