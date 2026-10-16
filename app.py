import os

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="PRIME FLOW", version="0.4.0")


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
        "version": "0.4.0",
        "status": "running",
        "trading": "order placement disabled",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/status")
def api_status():
    return {
        "application": "PRIME FLOW",
        "version": "0.4.0",
        "backend": "running",
        "order_placement": "disabled",
        "scanner": "not yet implemented",
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
        "connection_test": "not yet tested",
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
                "order_placement": "disabled",
            }

        raise HTTPException(
            status_code=502,
            detail=(
                "Dhan returned HTTP "
                f"{response.status_code}. Check token validity "
                "and API access in Dhan."
            ),
        )

    except httpx.RequestError as exc:
        # Never log exception text because it may expose sensitive headers.
        print(
            f"Dhan request failed: {type(exc).__name__}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Could not reach Dhan. No trade was placed.",
        )


@app.get("/api/scan")
def scan():
    raise HTTPException(
        status_code=503,
        detail=(
            "Scanner is not implemented yet. "
            "No trades have been placed."
        ),
    )


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
                    "Dhan LTP request failed with HTTP "
                    f"{response.status_code}. Check market-data API access."
                ),
            )

        data = response.json()

        return {
            "status": "success",
            "message": "Dhan returned an LTP response.",
            "data": data,
            "order_placement": "disabled",
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
