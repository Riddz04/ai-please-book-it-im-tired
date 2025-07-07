from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class BookingRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time: str  # ISO format datetime
    end_time: str    # ISO format datetime
    attendee_email: Optional[str] = None

class AvailabilityRequest(BaseModel):
    start_date: str  # ISO format date
    end_date: str    # ISO format date
    duration_minutes: int = 60

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    available: bool

class CalendarEvent(BaseModel):
    id: str
    title: str
    start_time: str
    end_time: str
    description: Optional[str] = ""
    attendees: Optional[List[str]] = []