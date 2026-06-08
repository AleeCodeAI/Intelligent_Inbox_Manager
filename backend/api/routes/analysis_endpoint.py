from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from database.analytics.emails_analysis import EmailsAnalysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/get-analysis")
@limiter.limit("100/minute")
async def endpoint_get_analysis(request: Request):
    """
    Triggers the email analysis to get analytical data for dashboard on frontend.
    """
    try:
        analyzer = EmailsAnalysis()
        results = analyzer.run_all_analysis()  

        logger.info("Analysis completed successfully")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": results,
            },
        )

    except Exception as e:
        logger.error(f"Failed to run analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run analysis: {str(e)}")