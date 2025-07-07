# 🚀 Deployment Guide - Railway

This guide will help you deploy your AI Calendar Booking Assistant to Railway.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **API Keys** (at least one):
   - **Groq API Key** (Recommended - Free): [console.groq.com](https://console.groq.com/)
   - **Google API Key** (Gemini): [makersuite.google.com](https://makersuite.google.com/app/apikey)
   - **OpenAI API Key** (Paid): [platform.openai.com](https://platform.openai.com/api-keys)

2. **Google Calendar Setup**:
   - Google Cloud Project with Calendar API enabled
   - Service Account JSON key file
   - Calendar shared with service account email

## 🚂 Railway Deployment Steps

### Step 1: Prepare Your Repository

1. **Add service account file to your repository**:
```bash
# Copy your service account file to the project root
cp /path/to/your/service-account-key.json ./service-account-key.json

# Add to git (be careful with sensitive files!)
git add service-account-key.json
git commit -m "Add service account key for deployment"
git push origin main
```

**⚠️ Security Note**: Only do this for deployment. For production, consider using Railway's secret management or environment variables.

### Step 2: Deploy to Railway

1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign up/Login** with your GitHub account
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select your repository**
5. **Railway will automatically detect** your `railway.toml` and `Dockerfile`

### Step 3: Configure Environment Variables

In your Railway dashboard, go to **Variables** tab and add:

```env
# Required: Choose one LLM provider
GROQ_API_KEY=your-groq-api-key-here

# Required: Google Calendar
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com
GOOGLE_SERVICE_ACCOUNT_FILE=./service-account-key.json

# Optional: Additional LLM providers
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
```

### Step 4: Alternative - Use Environment Variable for Service Account

If you prefer not to commit the file, you can use an environment variable:

1. **Convert JSON to base64**:
```bash
# On Mac/Linux:
base64 -i service-account-key.json

# On Windows:
certutil -encode service-account-key.json temp.b64 && findstr /v /c:- temp.b64
```

2. **Add to Railway Variables**:
```env
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=your-base64-encoded-json-here
```

3. **Update the backend code** to handle base64 (I'll show this in the next step)

### Step 5: Deploy

1. **Click Deploy** - Railway will build and deploy automatically
2. **Wait for deployment** (usually 2-3 minutes)
3. **Get your URL** from the Railway dashboard

## 🌐 Accessing Your Application

After deployment, Railway provides a single URL that serves both services:

- **Your App**: `https://your-app-name.up.railway.app` (Streamlit frontend on port 8501)
- **API Backend**: `https://your-app-name.up.railway.app:8000` (FastAPI backend)
- **API Docs**: `https://your-app-name.up.railway.app:8000/docs`

## 🔧 Alternative: Base64 Environment Variable Method

If you used the base64 method, here's how to update your backend:

1. **Update `backend/services/calendar_service.py`**:
```python
import base64
import json
import tempfile

def _authenticate(self):
    """Authenticate with Google Calendar API using service account"""
    
    # Try base64 environment variable first
    service_account_b64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64')
    if service_account_b64:
        try:
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
            
        except Exception as e:
            raise ValueError(f"Failed to decode service account from base64: {e}")
    
    # Fallback to file method
    elif os.path.exists(self.service_account_file):
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
    else:
        raise FileNotFoundError(f"Service account not found. Set GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 or place file at {self.service_account_file}")
```

## 🐛 Troubleshooting

### Common Issues:

1. **Backend Offline**:
   - Check Railway **Deployments** → **View Logs**
   - Verify API keys are set correctly in **Variables** tab
   - Ensure service account file exists or base64 is set

2. **Calendar Not Working**:
   - Verify `GOOGLE_CALENDAR_ID` is your actual calendar ID
   - Check service account has calendar access (share calendar with service account email)
   - Ensure Calendar API is enabled in Google Cloud Console

3. **LLM Errors**:
   - Verify API key is valid and has quota
   - Try Groq first (completely free)
   - Check Railway logs for specific error messages

### View Railway Logs:
1. Go to your Railway project dashboard
2. Click **Deployments** tab
3. Click on latest deployment
4. Click **View Logs**

## 💰 Cost Estimation

**Railway Costs**:
- **Hobby Plan**: $5/month (includes $5 usage credit)
- **Pro Plan**: $20/month (includes $20 usage credit)

**LLM Costs**:
- **Groq**: FREE (recommended)
- **Google Gemini**: FREE tier (15 req/min)
- **OpenAI**: ~$0.002 per 1K tokens

**Total Monthly Cost**: ~$5-20 (mostly Railway hosting)

## 🔄 Updates and Maintenance

To update your deployment:

1. **Push changes to GitHub**:
```bash
git add .
git commit -m "Update application"
git push origin main
```

2. **Railway auto-deploys** from your main branch

## 🎯 Production Tips

1. **Use Groq for cost-effective LLM** (completely free)
2. **Monitor Railway usage** in dashboard
3. **Set up custom domain** in Railway settings if needed
4. **Use Railway's built-in monitoring**
5. **Keep service account file secure** (consider base64 method for production)

## 📞 Support

If you encounter issues:

1. **Check Railway logs** in Deployments tab
2. **Review this deployment guide**
3. **Check the main README.md** for setup details
4. **Test locally first** with `python run_backend.py`

---

**🎉 Congratulations!** Your AI Calendar Booking Assistant is now live on Railway!

### Quick Test Commands:

```bash
# Test your deployed backend
curl https://your-app-name.up.railway.app:8000/

# Test chat endpoint
curl -X POST https://your-app-name.up.railway.app:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you check my availability?"}'
```