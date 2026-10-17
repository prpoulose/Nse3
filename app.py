
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="PRIME FLOW", version="0.5.0")

ORDER_PLACEMENT = "disabled"

CONDITIONS = [
    {"id": 1, "name": "Data connection"},
    {"id": 2, "name": "Global / event risk"},
    {"id": 3, "name": "India VIX"},
    {"id": 4, "name": "Today's price"},
    {"id": 5, "name": "Volume vs 5-day average"},
    {"id": 6, "name": "Open interest"},
    {"id": 7, "name": "Buyer / seller footprint"},
    {"id": 8, "name": "High-volume signal"},
    {"id": 9, "name": "EMA + RSI"},
    {"id": 10, "name": "5-day price + delivery"},
    {"id": 11, "name": "10-day support / resistance"},
    {"id": 12, "name": "News + impact"},
    {"id": 13, "name": "Final conclusion"},
]


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
def home():
    return {
        "application": "PRIME FLOW",
        "version": app.version,
        "status": "running",
        "trading": ORDER_PLACEMENT,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/status")
def api_status():
    return {
        "application": "PRIME FLOW",
        "version": app.version,
        "backend": "running",
        "scanner": "framework_ready_live_data_not_connected",
        "conditions": len(CONDITIONS),
        "order_placement": ORDER_PLACEMENT,
    }


@app.get("/api/dhan/status")
def dhan_status():
    return {
        "client_id_configured": bool(
            (os.getenv("DHAN_CLIENT_ID") or "").strip()
        ),
        "access_token_configured": bool(
            (os.getenv("DHAN_ACCESS_TOKEN") or "").strip()
        ),
        "connection_test": "run /api/dhan/test-connection",
        "order_placement": ORDER_PLACEMENT,
    }


@app.post("/api/dhan/test-connection")
def test_dhan_connection():
    headers = dhan_credentials()

    try:
        response = httpx.get(
            "https://api.dhan.co/v2/profile",
            headers=headers,
            timeout=15.0,
        )

        if response.status_code == 200:
            return {
                "status": "connected",
                "message": "Dhan connection successful.",
                "order_placement": ORDER_PLACEMENT,
            }

        raise HTTPException(
            status_code=502,
            detail=(
                f"Dhan returned HTTP {response.status_code}. "
                "Check token validity and API access in Dhan."
            ),
        )

    except httpx.RequestError as exc:
        print(f"Dhan request failed: {type(exc).__name__}", flush=True)
        raise HTTPException(
            status_code=502,
            detail="Could not reach Dhan. No trade was placed.",
        )


@app.get("/api/scan")
def scan():
    now = datetime.now(timezone.utc).isoformat()

    return {
        "application": "PRIME FLOW",
        "timestamp_utc": now,
        "status": "LIVE_DATA_UNAVAILABLE",
        "message": (
            "Scanner framework is ready, but live scanning has not "
            "been implemented or verified. No stock signals are generated."
        ),
        "conditions": [
            {
                **condition,
                "result": "UNAVAILABLE",
                "value": None,
                "reason": "Live data or validated analysis is not connected.",
            }
            for condition in CONDITIONS
        ],
        "qualified_stocks": 0,
        "minimum_target": 25,
        "results": [],
        "results_are_live": False,
        "order_placement": ORDER_PLACEMENT,
    }


@app.get("/api/dhan/test-ltp")
def test_dhan_ltp():
    headers = dhan_credentials()

    payload = {
        "NSE_EQ": [1333],
        "NSE_FNO": [],
        "BSE_EQ": [],
    }

    try:
        response = httpx.post(
            "https://api.dhan.co/v2/marketfeed/ltp",
            headers=headers,
            json=payload,
            timeout=15.0,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=(
                    f"Dhan LTP request failed with HTTP "
                    f"{response.status_code}. Check market-data API access."
                ),
            )

        return {
            "status": "success",
            "message": "Dhan returned an LTP response.",
            "data": response.json(),
            "order_placement": ORDER_PLACEMENT,
        }

    except httpx.RequestError as exc:
        print(
            f"Dhan LTP request failed: {type(exc).__name__}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Could not reach Dhan market-data API.",
        )
