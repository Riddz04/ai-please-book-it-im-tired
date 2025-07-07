import os
import base64
import json
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self):
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', './service-account-key.json')
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        self.service = None
        self.is_available = False
        
        # Try to authenticate, but don't fail if credentials are missing
        try:
            self.service = self._authenticate()
            self.is_available = True
            print("✅ Google Calendar service initialized successfully")
        except Exception as e:
            print(f"⚠️  Google Calendar not available: {e}")
            print("📝 To enable Google Calendar:")
            print("   1. Create a Google Cloud Project")
            print("   2. Enable Google Calendar API")
            print("   3. Create a Service Account and download JSON key")
            print("   4. Place the key file as 'service-account-key.json' in project root")
            print("   5. Set GOOGLE_CALENDAR_ID in your .env file")
            print("   6. Share your calendar with the service account email")
            self.is_available = False
        
    def _authenticate(self):
        """Authenticate with Google Calendar API using service account"""
        
        if not self.calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID not set in environment variables")
        
        # Try base64 environment variable first (for Railway deployment)
        service_account_b64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64')
        if service_account_b64:
            try:
                print("🔑 Using base64 service account from environment variable")
                # Decode base64 and create temporary file
                service_account_json = base64.b64decode(service_account_b64).decode('utf-8')
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(service_account_json)
                    temp_file_path = f.name
                
                credentials = service_account.Credentials.from_service_account_file(
                    temp_file_path,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                service = build('calendar', 'v3', credentials=credentials)
                
                # Test the connection
                service.calendars().get(calendarId=self.calendar_id).execute()
                
                return service
                
            except Exception as e:
                print(f"❌ Failed to use base64 service account: {e}")
                # Fall through to file method
        
        # Fallback to file method
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(f"Service account file not found: {self.service_account_file}. Set GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 environment variable or place file at {self.service_account_file}")
        
        try:
            print(f"🔑 Using service account file: {self.service_account_file}")
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            service = build('calendar', 'v3', credentials=credentials)
            
            # Test the connection
            service.calendars().get(calendarId=self.calendar_id).execute()
            
            return service
        except Exception as e:
            raise e
    
    def _check_availability(self):
        """Check if calendar service is available"""
        if not self.is_available:
            return False, "Google Calendar service is not available. Please check your credentials."
        return True, None
    
    def get_events(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get events from calendar within date range"""
        available, error = self._check_availability()
        if not available:
            print(f"Calendar not available: {error}")
            return []
        
        try:
            # Convert string dates to RFC3339 format
            start_time = datetime.fromisoformat(start_date).isoformat() + 'Z'
            end_time = datetime.fromisoformat(end_date).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start_time': start,
                    'end_time': end,
                    'description': event.get('description', ''),
                    'attendees': [attendee.get('email') for attendee in event.get('attendees', [])]
                })
            
            return formatted_events
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_availability(self, start_date: str, end_date: str, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get available time slots within date range"""
        available, error = self._check_availability()
        if not available:
            print(f"Calendar not available: {error}")
            # Return mock availability for demo purposes
            return self._get_mock_availability(start_date, end_date, duration_minutes)
        
        try:
            # Get existing events
            existing_events = self.get_events(start_date, end_date)
            
            # Generate potential time slots (9 AM to 5 PM, weekdays only)
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            available_slots = []
            current_date = start_dt.date()
            
            while current_date <= end_dt.date():
                # Skip weekends
                if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    # Generate hourly slots from 9 AM to 5 PM
                    for hour in range(9, 17):
                        slot_start = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                        slot_end = slot_start + timedelta(minutes=duration_minutes)
                        
                        # Check if slot conflicts with existing events
                        is_available = True
                        for event in existing_events:
                            event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                            event_end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
                            
                            # Convert to local timezone for comparison
                            if event_start.tzinfo:
                                event_start = event_start.replace(tzinfo=None)
                            if event_end.tzinfo:
                                event_end = event_end.replace(tzinfo=None)
                            
                            # Check for overlap
                            if (slot_start < event_end and slot_end > event_start):
                                is_available = False
                                break
                        
                        if is_available:
                            available_slots.append({
                                'start_time': slot_start.isoformat(),
                                'end_time': slot_end.isoformat(),
                                'available': True
                            })
                
                current_date += timedelta(days=1)
            
            return available_slots[:20]  # Limit to first 20 slots
        except Exception as e:
            print(f"Error getting availability: {e}")
            return self._get_mock_availability(start_date, end_date, duration_minutes)
    
    def _get_mock_availability(self, start_date: str, end_date: str, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Generate mock availability when calendar is not available"""
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        available_slots = []
        current_date = start_dt.date()
        
        while current_date <= end_dt.date() and len(available_slots) < 10:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Generate a few slots per day
                for hour in [9, 11, 14, 16]:  # 9 AM, 11 AM, 2 PM, 4 PM
                    slot_start = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                    slot_end = slot_start + timedelta(minutes=duration_minutes)
                    
                    available_slots.append({
                        'start_time': slot_start.isoformat(),
                        'end_time': slot_end.isoformat(),
                        'available': True
                    })
            
            current_date += timedelta(days=1)
        
        return available_slots[:10]
    
    def create_event(self, title: str, description: str, start_time: str, end_time: str, attendee_email: Optional[str] = None) -> Dict[str, Any]:
        """Create a new calendar event"""
        available, error = self._check_availability()
        if not available:
            # Return mock success for demo purposes
            return {
                'id': f'mock_event_{datetime.now().timestamp()}',
                'summary': title,
                'description': description,
                'start': {'dateTime': start_time},
                'end': {'dateTime': end_time},
                'status': 'mock_created'
            }
        
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if attendee_email and self.is_available:
                event['attendees'] = [{'email': attendee_email}]
            else:
                event['attendees'] = []  # Skip if demo mode or not supported

            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return created_event
        except HttpError as error:
            print(f'An error occurred: {error}')
            raise error
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        available, error = self._check_availability()
        if not available:
            return True  # Return success for mock events
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False