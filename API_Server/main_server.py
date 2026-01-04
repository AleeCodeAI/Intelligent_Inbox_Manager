from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import all your email processing classes
from basic_send import SendBasicEmail
from basic_delete import DeleteBasicEmail
from basic_get_all_emails import GetBasicEmails

from nonbusiness_send import NonBusinessSendEmail
from nonbusiness_delete import DeleteNonBusinessEmail
from nonbusiness_get_all_emails import GetNonBusinessEmails

from priority_send import SendPriorityEmail, CraftedEmail
from priority_delete import DeletePriorityEmail
from priority_get_all_emails import GetPriorityEmails

from scheduler_send import SchedulerSendEmail
from scheduler_delete import DeleteSchedulerEmail
from scheduler_get_all_emails import GetSchedulerEmails

# Initialize FastAPI app
app = FastAPI(
    title="Email Manager API",
    description="API for managing emails across different categories",
    version="1.0.0"
)

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request Models ====================

class EmailIdRequest(BaseModel):
    email_id: str

class SendEmailRequest(BaseModel):
    email_id: str
    crafted_message: str
    
class PriorityCraftedEmailRequest(BaseModel):
    email_id: str
    crafted_email: str
    classification: str
    start: Optional[str] = None  # ISO 8601 format from UI
    end: Optional[str] = None    # ISO 8601 format from UI

# ==================== Basic Email Endpoints ====================

@app.get("/basic/emails", tags=["Basic Emails"])
async def get_all_basic_emails():
    """Get all basic emails from the database"""
    try:
        getter = GetBasicEmails()
        emails = getter.get_all_emails()
        return {"count": len(emails), "emails": [email.model_dump() for email in emails]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/basic/email/{email_id}", tags=["Basic Emails"])
async def get_basic_email(email_id: str):
    """Get a specific basic email by ID"""
    try:
        getter = GetBasicEmails()
        email = getter.get_email_by_id(email_id)
        if email:
            return email.model_dump()
        raise HTTPException(status_code=404, detail="Email not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/basic/send", tags=["Basic Emails"])
async def send_basic_email(request: SendEmailRequest) -> Dict[str, Any]:
    """Send a basic email through n8n webhook"""
    try:
        sender = SendBasicEmail()
        result = sender.send_email(request.email_id, request.crafted_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/basic/delete", tags=["Basic Emails"])
async def delete_basic_email(request: EmailIdRequest) -> Dict[str, str]:
    """Delete a basic email from the database"""
    try:
        deleter = DeleteBasicEmail()
        deleter.delete_email(request.email_id)
        return {"status": "success", "message": f"Email {request.email_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Non-Business Email Endpoints ====================

@app.get("/nonbusiness/emails", tags=["Non-Business Emails"])
async def get_all_nonbusiness_emails():
    """Get all non-business emails from the database"""
    try:
        getter = GetNonBusinessEmails()
        emails = getter.get_all_emails()
        return {"count": len(emails), "emails": [email.model_dump() for email in emails]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nonbusiness/email/{email_id}", tags=["Non-Business Emails"])
async def get_nonbusiness_email(email_id: str):
    """Get a specific non-business email by ID"""
    try:
        getter = GetNonBusinessEmails()
        email = getter.get_email_by_id(email_id)
        if email:
            return email.model_dump()
        raise HTTPException(status_code=404, detail="Email not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nonbusiness/stats", tags=["Non-Business Emails"])
async def get_nonbusiness_stats():
    """Get statistics about non-business email classifications"""
    try:
        getter = GetNonBusinessEmails()
        stats = getter.get_classification_stats()
        total = getter.get_email_count()
        return {"total": total, "classifications": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nonbusiness/send", tags=["Non-Business Emails"])
async def send_nonbusiness_email(request: SendEmailRequest) -> Dict[str, Any]:
    """Send a non-business email through n8n webhook"""
    try:
        sender = NonBusinessSendEmail()
        result = sender.send_email(request.email_id, request.crafted_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/nonbusiness/delete", tags=["Non-Business Emails"])
async def delete_nonbusiness_email(request: EmailIdRequest) -> Dict[str, str]:
    """Delete a non-business email from the database"""
    try:
        deleter = DeleteNonBusinessEmail()
        deleter.delete_email(request.email_id)
        return {"status": "success", "message": f"Email {request.email_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Priority Email Endpoints ====================

@app.get("/priority/emails", tags=["Priority Emails"])
async def get_all_priority_emails():
    """Get all priority emails from the database"""
    try:
        getter = GetPriorityEmails()
        emails = getter.get_all_emails()
        return {"count": len(emails), "emails": [email.model_dump() for email in emails]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/priority/email/{email_id}", tags=["Priority Emails"])
async def get_priority_email(email_id: str):
    """Get a specific priority email by ID"""
    try:
        getter = GetPriorityEmails()
        email = getter.get_email_by_id(email_id)
        if email:
            return email.model_dump()
        raise HTTPException(status_code=404, detail="Email not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/priority/stats", tags=["Priority Emails"])
async def get_priority_stats():
    """Get statistics about priority email classifications"""
    try:
        getter = GetPriorityEmails()
        stats = getter.get_classification_stats()
        total = getter.get_email_count()
        return {"total": total, "classifications": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/priority/appointments", tags=["Priority Emails"])
async def get_appointments():
    """Get all appointment emails"""
    try:
        getter = GetPriorityEmails()
        appointments = getter.get_appointments()
        return {"count": len(appointments), "emails": [email.model_dump() for email in appointments]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/priority/send", tags=["Priority Emails"])
async def send_priority_email(request: PriorityCraftedEmailRequest) -> Dict[str, Any]:
    """
    Process and send a priority email (handles appointments with calendar events)
    
    For APPOINTMENT classification, start and end times are required.
    UI sends times in ISO 8601 format.
    
    Returns:
    - For successful sends: {"status": "success", "emailId": "...", "calendar": {"status": "confirmed", "id": "..."}}
    - For appointments: calendar object included if classification is APPOINTMENT
    - For failures: {"status": "failed", "reason": "...", ...}
    """
    try:
        crafted_email = CraftedEmail(
            email_id=request.email_id,
            crafted_email=request.crafted_email,
            classification=request.classification,
            start=request.start,
            end=request.end
        )
        sender = SendPriorityEmail()
        result = sender.process_email(crafted_email)
        print(f"[API] Result from process_email: {result}")  # Make sure this is there
        return result
    except Exception as e:
        return {
            "status": "failed",
            "reason": f"API error: {str(e)}",
            "emailId": None
        }

@app.delete("/priority/delete", tags=["Priority Emails"])
async def delete_priority_email(request: EmailIdRequest) -> Dict[str, str]:
    """Delete a priority email from the database"""
    try:
        deleter = DeletePriorityEmail()
        deleter.delete_email(request.email_id)
        return {"status": "success", "message": f"Email {request.email_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Scheduler Email Endpoints ====================

@app.get("/scheduler/emails", tags=["Scheduler Emails"])
async def get_all_scheduler_emails():
    """Get all scheduler emails from the database"""
    try:
        getter = GetSchedulerEmails()
        emails = getter.get_all_emails()
        return {"count": len(emails), "emails": [email.model_dump() for email in emails]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/email/{email_id}", tags=["Scheduler Emails"])
async def get_scheduler_email(email_id: str):
    """Get a specific scheduler email by ID"""
    try:
        getter = GetSchedulerEmails()
        email = getter.get_email_by_id(email_id)
        if email:
            return email.model_dump()
        raise HTTPException(status_code=404, detail="Email not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scheduler/send", tags=["Scheduler Emails"])
async def send_scheduler_email(request: SendEmailRequest) -> Dict[str, Any]:
    """Send a scheduler email through n8n webhook"""
    try:
        sender = SchedulerSendEmail()
        result = sender.send_email(request.email_id, request.crafted_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/scheduler/delete", tags=["Scheduler Emails"])
async def delete_scheduler_email(request: EmailIdRequest) -> Dict[str, str]:
    """Delete a scheduler email from the database"""
    try:
        deleter = DeleteSchedulerEmail()
        deleter.delete_email(request.email_id)
        return {"status": "success", "message": f"Email {request.email_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Health Check ====================

@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Email Manager API is running",
        "version": "1.0.0"
    }

# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)