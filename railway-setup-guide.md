# 🚂 Railway Setup Guide - Service Account File

Railway has updated their interface. Here are the current methods to handle your Google service account file:

## Method 1: Include File in Repository (Simplest)

1. **Copy your service account file to project root**:
```bash
cp /path/to/your/service-account-key.json ./service-account-key.json
```

2. **Add to git and push**:
```bash
git add service-account-key.json
git commit -m "Add service account for deployment"
git push origin main
```

3. **Deploy to Railway** - the file will be included in your build

⚠️ **Security Note**: Only do this for personal projects. For production, use Method 2.

## Method 2: Base64 Environment Variable (More Secure)

1. **Convert your JSON file to base64**:

**On Mac/Linux**:
```bash
base64 -i service-account-key.json
```

**On Windows**:
```bash
certutil -encode service-account-key.json temp.b64
type temp.b64 | findstr /v "CERTIFICATE"
```

2. **Copy the base64 output** (it will be a long string)

3. **In Railway dashboard**:
   - Go to your project
   - Click **Variables** tab
   - Add new variable:
     - **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64`
     - **Value**: Paste your base64 string

4. **The updated backend code** (already included) will automatically detect and use this

## Method 3: Railway CLI (Advanced)

If you have Railway CLI installed:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Set environment variable
railway variables set GOOGLE_SERVICE_ACCOUNT_JSON_BASE64="your-base64-string-here"
```

## ✅ Recommended Approach

**For this tutorial**: Use **Method 1** (include file in repo) - it's the simplest.

**For production apps**: Use **Method 2** (base64 environment variable) - it's more secure.

## 🔧 Environment Variables You Need

In Railway **Variables** tab, add:

```env
# Required: LLM API Key (choose one)
GROQ_API_KEY=your-groq-api-key-here

# Required: Google Calendar
GOOGLE_CALENDAR_ID=your-calendar-id@gmail.com

# Method 1: File path (if using file in repo)
GOOGLE_SERVICE_ACCOUNT_FILE=./service-account-key.json

# Method 2: Base64 (if using environment variable)
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=your-base64-encoded-json-here
```

## 🚀 Deploy Steps

1. **Push your code** to GitHub
2. **Connect to Railway** and deploy
3. **Add environment variables** in Railway dashboard
4. **Wait for deployment** to complete
5. **Test your app** at the provided URL

Your app will be available at: `https://your-app-name.up.railway.app`

## 🐛 Troubleshooting

If you see "Google Calendar not available":

1. **Check Railway logs**: Deployments → View Logs
2. **Verify environment variables** are set correctly
3. **Test your service account** locally first
4. **Ensure calendar is shared** with service account email

The app will work in demo mode even without Google Calendar, so you can test the LLM functionality first!