# 🤖 AI Calendar Booking Assistant

A conversational AI agent that helps users book appointments on Google Calendar through natural language chat. Built with FastAPI, Streamlit, and LangGraph.

## ✨ Features

- **Natural Language Processing**: Chat with the AI in plain English to book appointments
- **Google Calendar Integration**: Seamlessly connects to your Google Calendar using service account
- **Intelligent Scheduling**: Checks availability and suggests optimal time slots
- **Real-time Conversation**: Maintains context throughout the booking process
- **Beautiful UI**: Modern Streamlit interface with responsive design
- **Multiple LLM Support**: Works with Groq (free), Google Gemini, or OpenAI
- **Production Ready**: Containerized and ready for deployment

## 🛠 Tech Stack

- **Backend**: FastAPI with Python
- **Frontend**: Streamlit
- **AI Framework**: LangGraph + LangChain
- **LLM Options**: 
  - **Groq** (Recommended - Free and Fast)
  - **Google Gemini** (Generous free tier)
  - **OpenAI GPT-3.5** (Paid)
- **Calendar**: Google Calendar API
- **Deployment**: Docker, Railway, Render, Fly.io

## 🚀 Quick Start

### Prerequisites

1. **Google Calendar Setup**:
   - Create a Google Cloud Project
   - Enable Google Calendar API
   - Create a Service Account and download the JSON key file
   - Share your calendar with the service account email

2. **LLM API Key** (Choose one):
   - **Groq API Key** (Recommended - Free): Get from [https://console.groq.com/](https://console.groq.com/)
   - **Google API Key** (Gemini): Get from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - **OpenAI API Key** (Paid): Get from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Installation

1. **Clone and Setup**:
```bash
git clone <your-repo>
cd ai-calendar-booking
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Add Service Account Key**:
   - Place your `service-account-key.json` in the project root
   - Update `GOOGLE_SERVICE_ACCOUNT_FILE` path in `.env`

4. **Run the Application**:

**Backend** (Terminal 1):
```bash
python run_backend.py
```

**Frontend** (Terminal 2):
```bash
streamlit run frontend/streamlit_app.py
```

Visit: http://localhost:8501

## 🔧 Configuration

### Environment Variables

```env
# Google Calendar Configuration
GOOGLE_SERVICE_ACCOUNT_FILE=./service-account-key.json
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com

# LLM API Keys (choose one - Groq is recommended for free usage)
GROQ_API_KEY=your-groq-api-key          # FREE - Get from console.groq.com
GOOGLE_API_KEY=your-google-api-key      # FREE TIER - Get from makersuite.google.com
OPENAI_API_KEY=your-openai-api-key      # PAID - Get from platform.openai.com

# Backend Configuration
BACKEND_URL=http://localhost:8000
```

### Getting Free API Keys

#### Groq (Recommended - Completely Free)
1. Go to [https://console.groq.com/](https://console.groq.com/)
2. Sign up with your email
3. Go to API Keys section
4. Create a new API key
5. Copy and paste into your `.env` file as `GROQ_API_KEY`

#### Google Gemini (Generous Free Tier)
1. Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create API key
4. Copy and paste into your `.env` file as `GOOGLE_API_KEY`

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create Service Account:
   - Go to IAM & Admin > Service Accounts
   - Create new service account
   - Download JSON key file
5. Share your calendar:
   - Open Google Calendar
   - Settings > Share with specific people
   - Add service account email with "Make changes to events" permission

## 🐳 Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

### Manual Docker Build

```bash
docker build -t ai-booking-app .
docker run -p 8000:8000 -p 8501:8501 ai-booking-app
```

## ☁️ Cloud Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Upload `service-account-key.json` as a file
4. Deploy automatically

### Render

1. Connect repository to Render
2. Use the provided `render.yaml` configuration
3. Add environment variables
4. Deploy both backend and frontend services

### Fly.io

```bash
fly launch
fly secrets set GROQ_API_KEY=your-key
fly secrets set GOOGLE_CALENDAR_ID=your-calendar-id
fly deploy
```

## 💬 Usage Examples

**Check Availability**:
- "What's my availability this week?"
- "Do I have any free time tomorrow afternoon?"

**Book Appointments**:
- "Book a meeting with John tomorrow at 2 PM"
- "Schedule a 30-minute call for Friday morning"
- "I need to book a doctor's appointment next week"

**View Events**:
- "What meetings do I have today?"
- "Show me my schedule for next week"

## 🔧 API Endpoints

- `POST /chat` - Send messages to AI agent
- `POST /availability` - Check calendar availability
- `POST /book` - Book new appointment
- `GET /events` - Get existing events
- `DELETE /events/{event_id}` - Cancel event

## 🧪 Testing

The AI agent includes comprehensive conversation handling:

- **Context Awareness**: Remembers previous conversation
- **Confirmation**: Always confirms before booking
- **Error Handling**: Graceful error messages
- **Validation**: Checks for conflicts and availability

## 🔒 Security

- Service account authentication (no OAuth required)
- Environment variable protection
- Input validation and sanitization
- CORS configuration for production

## 💰 Cost Comparison

| Provider | Cost | Rate Limits | Notes |
|----------|------|-------------|-------|
| **Groq** | **FREE** | 30 requests/minute | Fastest, completely free |
| **Google Gemini** | **FREE** (15 req/min) | 15 requests/minute free | Generous free tier |
| **OpenAI** | **$0.002/1K tokens** | Pay per use | Most expensive |

**Recommendation**: Use Groq for development and testing, consider Gemini for production.

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Google Calendar API documentation
3. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, Streamlit, and LangGraph**