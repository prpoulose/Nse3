
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

APP_NAME = "PRIME FLOW Backend"
DHAN_BASE_URL = "https://api.dhan.co/v2"

app = FastAPI(
    title=APP_NAME,
    version="0.4.0",
    description="PRIME FLOW NSE F&O scanner backend",
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


def dhan_credentials():
    client_id = (os.getenv("DHAN_CLIENT_ID") or "").strip()
    access_token = (os.getenv("DHAN_ACCESS_TOKEN") or "").strip()

    if not client_id or not access_token:
        raise HTTPException(
            status_code=503,
            detail="Dhan credentials are missing in Render Environment.",
        )

    return {
        "client-id": client_id,
        "access-token": access_token,
        "Content-Type": "application/json",
    }


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "status": "running",
        "market_data": "NOT_CONNECTED",
        "utc_time": utc_now(),
        "order_placement": "DISABLED",
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
        "market_data": "NOT_VERIFIED",
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
            "11_data_status": "BACKEND_ONLINE",
            "12_global_market_and_events": "NOT_CONNECTED",
        },
    }


@app.get("/api/dhan/status")
def dhan_status():
    return {
        "service": APP_NAME,
        "client_id_configured": bool(
            (os.getenv("DHAN_CLIENT_ID") or "").strip()
        ),
        "access_token_configured": bool(
            (os.getenv("DHAN_ACCESS_TOKEN") or "").strip()
        ),
        "authentication_test": "NOT_RUN",
        "market_data": "NOT_VERIFIED",
        "scanner": "NOT_IMPLEMENTED",
        "order_placement": "DISABLED",
    }


@app.post("/api/dhan/test-connection")
def dhan_test_connection():
    headers = dhan_credentials()

    try:
        response = httpx.get(
            f"{DHAN_BASE_URL}/profile",
            headers=headers,
            timeout=15.0,
        )

        if response.status_code == 200:
            return {
                "service": APP_NAME,
                "authentication_test": "SUCCESS",
                "message": "Dhan accepted the credentials.",
                "market_data": "NOT_TESTED",
                "scanner": "NOT_IMPLEMENTED",
                "order_placement": "DISABLED",
                "tested_at_utc": utc_now(),
            }

        if response.status_code in (401, 403):
            raise HTTPException(
                status_code=401,
                detail=(
                    "Dhan rejected the credentials. Check token validity "
                    "and API access. No trade was placed."
                ),
            )

        print(
            f"Dhan profile returned HTTP {response.status_code}.",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                f"Dhan returned HTTP {response.status_code}. "
                "No trade was placed."
            ),
        )

    except HTTPException:
        raise
    except httpx.TimeoutException as exc:
        print(
            f"Dhan connection timeout: {type(exc).__name__}",
            flush=True,
        )
        raise HTTPException(
            status_code=504,
            detail="Dhan connection timed out. No trade was placed.",
        )
    except httpx.RequestError as exc:
        # Never print the exception text; it may contain sensitive headers.
        print(
            f"Dhan request failed: {type(exc).__name__}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Could not reach Dhan. No trade was placed.",
        )


@app.post("/api/scan")
def scan():
    raise HTTPException(
        status_code=503,
        detail=(
            "Scanner is not ready. Market data and scanner logic "
            "must be implemented and verified first. "
            "No signals were generated and no trade was placed."
        ),
    )
