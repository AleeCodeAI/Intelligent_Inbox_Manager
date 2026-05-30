import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import (
    get_all_emails,
    get_all_email_processing,
    get_all_appointments,
    get_basic_manual_pending,
    get_nonbusiness_unreviewed,
    get_priority_unreviewed,
)

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _serialize(data: Any) -> Any:
    """Recursively convert datetime objects to ISO strings for JSON serialization."""
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, dict):
        return {k: _serialize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_serialize(i) for i in data]
    return data


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/emails")
@limiter.limit("30/minute")
async def endpoint_get_all_emails(request: Request):
    """
    All emails from the main emails table.
    Used in the analysis dashboard.
    """
    try:
        data = get_all_emails()
        logger.info(f"Fetched {len(data)} emails")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


@router.get("/email-processing")
@limiter.limit("30/minute")
async def endpoint_get_all_email_processing(request: Request):
    """
    All records from the email_processing table joined with emails.
    Used in the analysis dashboard.
    """
    try:
        data = _serialize(get_all_email_processing())
        logger.info(f"Fetched {len(data)} email processing records")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch email processing records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch email processing records: {str(e)}")


@router.get("/appointments")
@limiter.limit("30/minute")
async def endpoint_get_all_appointments(request: Request):
    """
    All appointments joined with their originating email.
    """
    try:
        data = _serialize(get_all_appointments())
        logger.info(f"Fetched {len(data)} appointments")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch appointments: {str(e)}")


@router.get("/basic/manual-pending")
@limiter.limit("30/minute")
async def endpoint_get_basic_manual_pending(request: Request):
    """
    Basic emails where RAG failed and manual reply is pending.
    Returns emails where needs_manual_reply=True and reviewed=False.
    """
    try:
        data = get_basic_manual_pending()
        logger.info(f"Fetched {len(data)} basic manual-pending emails")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch basic manual-pending emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch basic manual-pending emails: {str(e)}")


@router.get("/nonbusiness/unreviewed")
@limiter.limit("30/minute")
async def endpoint_get_nonbusiness_unreviewed(request: Request):
    """
    Non-business emails that have not yet been reviewed by admin.
    Ordered by confidence descending.
    """
    try:
        data = get_nonbusiness_unreviewed()
        logger.info(f"Fetched {len(data)} unreviewed non-business emails")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch unreviewed non-business emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch unreviewed non-business emails: {str(e)}")


@router.get("/priority/unreviewed")
@limiter.limit("30/minute")
async def endpoint_get_priority_unreviewed(request: Request):
    """
    High-priority emails that have not yet been reviewed by admin.
    Ordered by confidence descending.
    """
    try:
        data = get_priority_unreviewed()
        logger.info(f"Fetched {len(data)} unreviewed priority emails")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "count": len(data), "data": data},
        )
    except Exception as e:
        logger.error(f"Failed to fetch unreviewed priority emails: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch unreviewed priority emails: {str(e)}")