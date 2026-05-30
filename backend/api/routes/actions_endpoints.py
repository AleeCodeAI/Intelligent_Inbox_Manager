from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from flows import PriorityAction, NonBusinessAction
from schemas import PriorityAction as PriorityActionSchema, NonBusinessAction as NonBusinessActionSchema

router = APIRouter(prefix="/actions", tags=["Actions"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


# ============================================================
# Priority Action
# ============================================================
@router.post("/priority-action")
@limiter.limit("30/minute")
async def endpoint_priority_action(request: Request, data: PriorityActionSchema):
    try:
        action = PriorityAction()
        logger.info(f"Taking action for priority email with Gmail ID: {data.gmail_id}")
        result = action.run(data)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result}
        )
    except Exception as e:
        logger.error(f"Failed to take action for priority email {data.gmail_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to take action for priority email: {str(e)}")
    

# ============================================================
# NonBusiness Action
# ============================================================
@router.post("/nonbusiness-action")
@limiter.limit("30/minute")
async def endpoint_nonbusiness_action(request: Request, data: NonBusinessActionSchema):
    try:
        action = NonBusinessAction()
        logger.info(f"Taking action for nonbusiness email with Gmail ID: {data.gmail_id}")
        result = action.run(data)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result}
        )
    except Exception as e:
        logger.error(f"Failed to take action for nonbusiness email {data.gmail_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to take action for nonbusiness email: {str(e)}")