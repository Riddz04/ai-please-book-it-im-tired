import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Page configuration
st.set_page_config(
    page_title="AI Calendar Booking Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2rem;
        border-radius: 12px;
        color: #fff;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Chat bubbles */
    .chat-container {
        background: #1e1e2f;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #6366f1;
    }

    .user-message {
        background: #2e2e42;
        color: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 5px solid #3b82f6;
    }

    .ai-message {
        background: #37304a;
        color: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 5px solid #a855f7;
    }

    /* Sidebar layout */
    .sidebar-content {
        background: #1c1c2e;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2f2f45;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .status-indicator {
        padding: 0.6rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .status-online {
        background: #d1fae5;
        color: #065f46;
        border: 1px solid #10b981;
    }

    .status-offline {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #f87171;
    }

    /* Chat input */
    .stChatInput input {
        background-color: #1e1e2f !important;
        color: #ffffff !important;
        border: 1px solid #4b5563;
        padding: 0.75rem;
        border-radius: 8px;
    }

    .stChatInput input::placeholder {
        color: #9ca3af;
    }

    /* Buttons */
    .stButton>button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 10px;
        padding: 0.65rem 1.2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }

    .stButton>button:hover {
        background-color: #4f46e5 !important;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }

    /* Date pickers */
    .stDateInput>div>input {
        background-color: #2e2e42;
        color: #fff;
        border-radius: 6px;
        padding: 0.4rem 0.6rem;
        border: 1px solid #4b5563;
    }

    .stDateInput>label {
        font-weight: 500;
        font-size: 0.9rem;
        color: #e5e7eb;
    }

    /* Markdown and form elements */
    .stMarkdown, .stTextInput, .stDateInput label {
        color: white;
        font-size: 0.95rem;
    }

    .stSubheader {
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.05rem;
        font-weight: 600;
    }

    hr {
        border-top: 1px solid #3b3b50;
    }
</style>
""", unsafe_allow_html=True)



def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_chat_message(message, session_id=None):
    """Send message to AI agent"""
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "context": {}
        }
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"response": f"Error: {response.status_code} - {response.text}", "session_id": session_id}
    except Exception as e:
        return {"response": f"Connection error: {str(e)}", "session_id": session_id}

def get_availability(start_date, end_date, duration=60):
    """Get calendar availability"""
    try:
        payload = {
            "start_date": start_date,
            "end_date": end_date,
            "duration_minutes": duration
        }
        response = requests.post(f"{BACKEND_URL}/availability", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["availability"]
        return []
    except:
        return []

def get_events(start_date, end_date):
    """Get existing events"""
    try:
        response = requests.get(f"{BACKEND_URL}/events", params={
            "start_date": start_date,
            "end_date": end_date
        }, timeout=15)
        if response.status_code == 200:
            return response.json()["events"]
        return []
    except:
        return []

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().timestamp()}"

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Calendar Booking Assistant</h1>
    <p>Your intelligent assistant for scheduling appointments and managing your calendar</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    st.header("🔧 System Status")
    
    # Backend status
    backend_online = check_backend_status()
    if backend_online:
        st.markdown('<div class="status-indicator status-online">✅ Backend Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-offline">❌ Backend Offline</div>', unsafe_allow_html=True)
        st.error("Please ensure the backend server is running on port 8000")
    
    st.header("📊 Quick Actions")
    
    # Quick availability check
    st.subheader("Check Availability")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date())
    with col2:
        end_date = st.date_input("End Date", (datetime.now() + timedelta(days=7)).date())
    
    if st.button("🔍 Check Availability", use_container_width=True):
        if backend_online:
            with st.spinner("Checking availability..."):
                availability = get_availability(start_date.isoformat(), end_date.isoformat())
                if availability:
                    st.success(f"Found {len(availability)} available slots!")
                    for slot in availability[:5]:
                        start_time = datetime.fromisoformat(slot['start_time'])
                        st.write(f"• {start_time.strftime('%A, %B %d at %I:%M %p')}")
                else:
                    st.warning("No available slots found.")
        else:
            st.error("Backend not available")
    
    # View existing events
    st.subheader("Existing Events")
    if st.button("📅 View Events", use_container_width=True):
        if backend_online:
            with st.spinner("Loading events..."):
                events = get_events(start_date.isoformat(), end_date.isoformat())
                if events:
                    st.success(f"Found {len(events)} events")
                    for event in events[:5]:
                        start_time = datetime.fromisoformat(event['start_time'].replace('Z', ''))
                        st.write(f"• {event['title']} - {start_time.strftime('%m/%d at %I:%M %p')}")
                else:
                    st.info("No events found.")
        else:
            st.error("Backend not available")
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{datetime.now().timestamp()}"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface
st.header("💬 Chat with AI Assistant")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message"><strong>AI Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
if backend_online:
    # Example prompts
    st.subheader("💡 Try these examples:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Check my availability this week", use_container_width=True):
            example_message = "Can you check my availability for this week?"
            st.session_state.messages.append({"role": "user", "content": example_message})
            with st.spinner("AI is thinking..."):
                response = send_chat_message(example_message, st.session_state.session_id)
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.session_state.session_id = response["session_id"]
            st.rerun()
    
    with col2:
        if st.button("🤝 Book a meeting tomorrow", use_container_width=True):
            example_message = "I need to book a meeting for tomorrow afternoon"
            st.session_state.messages.append({"role": "user", "content": example_message})
            with st.spinner("AI is thinking..."):
                response = send_chat_message(example_message, st.session_state.session_id)
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.session_state.session_id = response["session_id"]
            st.rerun()
    
    with col3:
        if st.button("📋 Show my events", use_container_width=True):
            example_message = "What events do I have coming up?"
            st.session_state.messages.append({"role": "user", "content": example_message})
            with st.spinner("AI is thinking..."):
                response = send_chat_message(example_message, st.session_state.session_id)
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                st.session_state.session_id = response["session_id"]
            st.rerun()
    
    # Chat input
    user_input = st.chat_input("Type your message here... (e.g., 'Book a meeting for tomorrow at 2 PM')")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("AI is thinking..."):
            response = send_chat_message(user_input, st.session_state.session_id)
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            st.session_state.session_id = response["session_id"]
        
        st.rerun()

else:
    st.error("🚫 Backend server is not available. Please start the backend server first.")
    st.info("Run: `uvicorn backend.main:app --reload` in your terminal")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 AI Calendar Booking Assistant | Built with FastAPI, Streamlit & LangGraph</p>
    <p>💡 Ask me to check availability, book meetings, or view your calendar!</p>
</div>
""", unsafe_allow_html=True)