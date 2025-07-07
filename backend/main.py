from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import uvicorn

from backend.services.calendar_service import CalendarService
from backend.services.ai_agent import AIBookingAgent
from backend.models.booking_models import ChatMessage, BookingRequest, AvailabilityRequest

load_dotenv()

app = FastAPI(title="AI Calendar Booking API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
calendar_service = CalendarService()
ai_agent = AIBookingAgent(calendar_service)

@app.get("/")
async def root():
    return {"message": "AI Calendar Booking API is running"}

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Handle chat messages and return AI agent response"""
    try:
        response = await ai_agent.process_message(
            message.message, 
            message.session_id,
            message.context
        )
        return {"response": response, "session_id": message.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/availability")
async def check_availability(request: AvailabilityRequest):
    """Check calendar availability for given date range"""
    try:
        availability = calendar_service.get_availability(
            request.start_date,
            request.end_date,
            request.duration_minutes
        )
        return {"availability": availability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book")
async def book_appointment(booking: BookingRequest):
    """Book an appointment"""
    try:
        event = calendar_service.create_event(
            booking.title,
            booking.description,
            booking.start_time,
            booking.end_time,
            booking.attendee_email
        )
        return {"success": True, "event_id": event.get('id'), "event": event}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
async def get_events(start_date: str, end_date: str):
    """Get events in date range"""
    try:
        events = calendar_service.get_events(start_date, end_date)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
async def cancel_event(event_id: str):
    """Cancel an event"""
    try:
        result = calendar_service.delete_event(event_id)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)