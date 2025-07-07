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

1. **Push to GitHub**:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign up/Login** with your GitHub account
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select your repository**
5. **Railway will automatically detect** your `railway.toml` and `Dockerfile`

### Step 3: Configure Environment Variables

In your Railway dashboard, go to **Variables** and add:

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

### Step 4: Upload Service Account Key

1. In Railway dashboard, go to **Settings** → **Environment**
2. **Upload Files** → Select your `service-account-key.json`
3. The file will be available at `./service-account-key.json` in the container

### Step 5: Deploy

1. **Click Deploy** - Railway will build and deploy automatically
2. **Wait for deployment** (usually 2-3 minutes)
3. **Get your URL** from the Railway dashboard

## 🌐 Accessing Your Application

After deployment, you'll get a URL like: `https://your-app-name.up.railway.app`

- **Frontend (Streamlit)**: `https://your-app-name.up.railway.app:8501`
- **Backend (FastAPI)**: `https://your-app-name.up.railway.app:8000`
- **API Docs**: `https://your-app-name.up.railway.app:8000/docs`

## 🔧 Post-Deployment Configuration

### Update Frontend Backend URL

The frontend needs to know your backend URL. Railway automatically sets this via the `BACKEND_URL` environment variable in `railway.toml`.

### Test Your Deployment

1. **Visit your frontend URL**
2. **Check system status** in the sidebar
3. **Try example prompts**:
   - "Check my availability this week"
   - "Book a meeting tomorrow at 2 PM"

## 🐛 Troubleshooting

### Common Issues:

1. **Backend Offline**:
   - Check Railway logs for errors
   - Verify API keys are set correctly
   - Ensure service account file is uploaded

2. **Calendar Not Working**:
   - Verify `GOOGLE_CALENDAR_ID` is correct
   - Check service account has calendar access
   - Ensure Calendar API is enabled in Google Cloud

3. **LLM Errors**:
   - Verify API key is valid and has quota
   - Try switching to Groq (free) if using paid services
   - Check Railway logs for specific error messages

### View Logs:
```bash
# In Railway dashboard, go to Deployments → View Logs
```

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
3. **Set up custom domain** in Railway settings
4. **Enable Railway's built-in monitoring**
5. **Use environment-specific configs** for staging/production

## 📞 Support

If you encounter issues:

1. **Check Railway logs** first
2. **Review this deployment guide**
3. **Check the main README.md** for setup details
4. **Open an issue** on GitHub if problems persist

---

**🎉 Congratulations!** Your AI Calendar Booking Assistant is now live on Railway!