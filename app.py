
import os
from datetime import datetime, timezone

import pyotp
from SmartApi import SmartConnect

from fastapi import FastAPI, HTTPException, Header
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

 

@app.get("/api/angel/test-login")
def angel_test_login(
    x_angel_test_key: str | None = Header(default=None),
):
    expected_key = os.getenv("ANGEL_TEST_KEY")

    if (
        not expected_key
        or not x_angel_test_key
        or x_angel_test_key != expected_key
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    api_key = os.getenv("ANGEL_API_KEY")
    client_id = os.getenv("ANGEL_CLIENT_ID")
    mpin = os.getenv("ANGEL_MPIN")
    totp_secret = os.getenv("ANGEL_TOTP_SECRET")

    if not all([api_key, client_id, mpin, totp_secret]):
        raise HTTPException(
            status_code=503,
            detail="Angel One settings are missing in Render.",
        )

    smart_api = None

    try:
        smart_api = SmartConnect(api_key=api_key)
        totp_code = pyotp.TOTP(totp_secret).now()

        session = smart_api.generateSession(
            client_id,
            mpin,
            totp_code,
        )

        if not session or not session.get("status"):
            raise HTTPException(
                status_code=401,
                detail=(
                    "Angel One authentication failed. "
                    "Check credentials and TOTP settings."
                ),
            )

        return {
            "service": APP_NAME,
            "security_check": "SUCCESS",
            "authentication_test": "SUCCESS",
            "market_data": "NOT_CONNECTED",
            "order_placement": "DISABLED",
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=(
                "Angel One authentication could not be completed. "
                "Check Render logs without sharing credentials."
            ),
        )

    finally:
        if smart_api is not None:
            try:
                smart_api.terminateSession(client_id)
            except Exception:
                pass

