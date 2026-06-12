from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database import delete_email
from flows import DeleteAppointment
from schemas import DeleteAppointment as DeleteAppointmentSchema

router = APIRouter(prefix="/delete", tags=["Delete"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.delete("/email/{gmail_id}")
@limiter.limit("30/minute")
async def endpoint_delete_email(request: Request, gmail_id: str):
    """
    Takes a gmail_id and deletes the email.
    Cascades to all extension tables automatically.
    """
    try:
        delete_email(gmail_id)
        logger.info(f"Deleted email with Gmail ID: {gmail_id}")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "deleted_gmail_id": gmail_id},
        )
    except Exception as e:
        logger.error(f"Failed to delete email {gmail_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {str(e)}")


@router.delete("/appointment/{gmail_id}/{event_id}")  
@limiter.limit("30/minute")
async def endpoint_delete_appointment(
    request: Request, 
    gmail_id: str,  
    event_id: str   
):
    """
    Takes gmail_id and event_id as path parameters.
    Deletes the email from the database (cascades automatically)
    and removes the corresponding calendar event via n8n.
    """
    try:
        # Create schema object from path parameters
        data = DeleteAppointmentSchema(gmail_id=gmail_id, event_id=event_id)
        delete_flow = DeleteAppointment()
        delete_flow.delete_appointment(data)
        
        logger.info(f"Successfully deleted appointment. Gmail ID: {gmail_id} | Event ID: {event_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success", 
                "deleted_gmail_id": gmail_id,
                "deleted_event_id": event_id
            },
        )
    except Exception as e:
        logger.error(f"Failed to execute appointment deletion sequence: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete appointment sequence: {str(e)}"
        )