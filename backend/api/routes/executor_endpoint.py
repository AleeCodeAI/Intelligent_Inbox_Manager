from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from core.executor import Executor

router = APIRouter(prefix="/master-pipeline", tags=["Master"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/executor-run")
@limiter.limit("10/minute")
async def endpoint_run_executor(request: Request):
    """
    Triggers the master pipeline executor.
    Fetches unprocessed emails and runs them through the full pipeline.
    """
    try:
        executor = Executor()
        results = await executor.run()

        logger.info(f"Executor finished — processed {len(results)} emails")

        data = [
            {
                "gmail_id": result.gmail_id,
                "classification": result.result.classification,
                "success": result.success,
            }
            for result in results
        ]

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "processed_count": len(data),
                "results": data,
            },
        )

    except Exception as e:
        logger.error(f"Failed to run executor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run executor: {str(e)}")