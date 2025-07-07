import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory

# LLM imports with fallbacks
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Groq not available. Install with: pip install langchain-groq")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google GenAI not available. Install with: pip install langchain-google-genai")

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available. Install with: pip install langchain-openai")

from backend.services.calendar_service import CalendarService


class AIBookingAgent:
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
        self.llm = self._initialize_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.sessions = {}

    def _initialize_llm(self):
        if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
            try:
                print("✅ Using Groq LLM (Free)")
                return ChatGroq(
                    model="llama3-70b-8192",
                    temperature=0.7,
                    groq_api_key=os.getenv('GROQ_API_KEY')
                )
            except Exception as e:
                print(f"❌ Groq initialization failed: {e}")

        elif GOOGLE_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
            try:
                print("✅ Using Google Gemini LLM (Free Tier)")
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=os.getenv('GOOGLE_API_KEY'),
                    temperature=0.7
                )
            except Exception as e:
                print(f"❌ Google Gemini initialization failed: {e}")

        elif OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                print("✅ Using OpenAI LLM (Paid)")
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.7,
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
            except Exception as e:
                print(f"❌ OpenAI initialization failed: {e}")

        raise ValueError(f"""
🚫 No valid LLM API key found! 

Please set one of the following environment variables in your .env file:

1. GROQ_API_KEY (Recommended, Free) - https://console.groq.com/
2. GOOGLE_API_KEY (Free Tier) - https://makersuite.google.com/app/apikey
3. OPENAI_API_KEY (Paid) - https://platform.openai.com/api-keys

Available packages:
- Groq: {GROQ_AVAILABLE}
- Google: {GOOGLE_AVAILABLE}  
- OpenAI: {OPENAI_AVAILABLE}

Current environment variables:
- GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set'}
- GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}
- OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}
        """)

    def _create_tools(self) -> List[Tool]:
        def parse_date_range(input_str: str) -> Tuple[str, str]:
            try:
                if not input_str or not isinstance(input_str, str):
                    raise ValueError("Empty or invalid input")
                input_str = input_str.strip().replace('"', '').replace("'", "")
                if 'to' in input_str:
                    start, end = input_str.split('to')
                    return start.strip(), end.strip()
            except:
                pass
            today = datetime.now().strftime('%Y-%m-%d')
            future = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            return today, future

        def check_availability_tool(date_range: str) -> str:
            try:
                start_date, end_date = parse_date_range(date_range)
                availability = self.calendar_service.get_availability(start_date, end_date)
                if not availability:
                    return "No available slots found for the specified date range."

                calendar_note = ""
                if not self.calendar_service.is_available:
                    calendar_note = "\n\n📝 Note: Showing demo availability (Google Calendar not connected)"

                slots_text = "Available time slots:\n"
                for i, slot in enumerate(availability[:10], 1):
                    start_time = datetime.fromisoformat(slot['start_time'])
                    slots_text += f"{i}. {start_time.strftime('%A, %B %d at %I:%M %p')}\n"

                return slots_text + calendar_note
            except Exception as e:
                return f"Error checking availability: {str(e)}"

        def book_appointment_tool(booking_details: str) -> str:
            try:
                parts = booking_details.split('|')
                if len(parts) < 4:
                    return "Invalid booking format. Please provide: title|description|start_time|end_time|email"

                title = parts[0].strip()
                description = parts[1].strip()
                start_time = parts[2].strip()
                end_time = parts[3].strip()
                email = parts[4].strip() if len(parts) > 4 else None

                if 'T' not in start_time:
                    start_time += 'T00:00:00'
                if 'T' not in end_time:
                    end_time += 'T00:00:00'

                # Validate ISO format
                datetime.fromisoformat(start_time)
                datetime.fromisoformat(end_time)

                event = self.calendar_service.create_event(
                    title, description, start_time, end_time, email
                )

                calendar_note = ""
                if not self.calendar_service.is_available:
                    calendar_note = "\n\n📝 Note: This is a demo booking (Google Calendar not connected)"

                return f"✅ Appointment booked successfully! Event ID: {event.get('id')}" + calendar_note
            except Exception as e:
                return f"Error booking appointment: {str(e)}"

        def get_existing_events_tool(date_range: str) -> str:
            try:
                start_date, end_date = parse_date_range(date_range)
                events = self.calendar_service.get_events(start_date, end_date)
                if not events:
                    calendar_note = ""
                    if not self.calendar_service.is_available:
                        calendar_note = "\n\n📝 Note: No events shown (Google Calendar not connected)"
                    return "No existing events found for the specified date range." + calendar_note

                events_text = "Existing events:\n"
                for event in events:
                    start_time = datetime.fromisoformat(event['start_time'].replace('Z', ''))
                    events_text += f"• {event['title']} - {start_time.strftime('%A, %B %d at %I:%M %p')}\n"

                return events_text
            except Exception as e:
                return f"Error getting events: {str(e)}"

        return [
            Tool(
                name="check_availability",
                description="Check calendar availability for booking appointments.",
                func=check_availability_tool
            ),
            Tool(
                name="book_appointment",
                description="Book a new appointment. Format: title|description|start_time|end_time|email",
                func=book_appointment_tool
            ),
            Tool(
                name="get_existing_events",
                description="Fetch existing events from calendar for a given date range.",
                func=get_existing_events_tool
            )
        ]

    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["input", "tools", "tool_names", "chat_history", "current_date", "agent_scratchpad"],
            template="""
You are a helpful AI assistant specialized in booking calendar appointments.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer  
Thought: you should always think about what to do  
Action: the action to take, should be one of [{tool_names}]  
Action Input: the input to the action  
Observation: the result of the action  
... (this Thought/Action/Action Input/Observation can repeat N times)  
Thought: I now know the final answer  
Final Answer: the final answer to the original input question

If you need more information from the user, stop and ask them clearly using Final Answer. Do not try to call tools again after asking a question.

Avoid using Python code syntax like `.remove()` or comments like `# this is ...` in action inputs. Just pass plain text.

Be conversational, friendly, and helpful. Always confirm details before booking.

Current date: {current_date}

Previous conversation:
{chat_history}

Question: {input}  
Thought: {agent_scratchpad}
"""
        )

        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="force"
        )

    async def process_message(self, message: str, session_id: str = None, context: Dict[str, Any] = None) -> str:
        try:
            if not session_id:
                session_id = f"session_{datetime.now().timestamp()}"

            if session_id not in self.sessions:
                self.sessions[session_id] = ChatMessageHistory()

            chat_history = self.sessions[session_id]

            history_text = ""
            for msg in chat_history.messages[-6:]:
                if isinstance(msg, HumanMessage):
                    history_text += f"Human: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    history_text += f"Assistant: {msg.content}\n"

            current_date = datetime.now().strftime('%Y-%m-%d')

            response = await self.agent.ainvoke({
                "input": message,
                "chat_history": history_text,
                "current_date": current_date
            })

            chat_history.add_user_message(message)
            if "output" in response:
                chat_history.add_ai_message(response["output"])
                return response["output"]
            else:
                return "⚠️ Unexpected response format from LLM agent."

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            if "API key" in str(e).lower() or "invalid_api_key" in str(e).lower():
                error_msg = """🔑 API Key Error!

It looks like there's an issue with your API key. Please check your .env file:

- GROQ_API_KEY (Free): https://console.groq.com/
- GOOGLE_API_KEY (Free Tier): https://makersuite.google.com/app/apikey
- OPENAI_API_KEY (Paid): https://platform.openai.com/api-keys

Then restart the backend:
```bash
python run_backend.py
```"""
            elif "quota" in str(e).lower():
                error_msg += "\n\n💰 This looks like a quota/billing issue. Consider switching to Groq or Google Gemini."
            elif "rate limit" in str(e).lower():
                error_msg += "\n\n⏱️ Rate limit exceeded. Please wait a moment and try again."

            return error_msg
