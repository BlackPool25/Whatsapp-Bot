# WhatsApp Bot - Cleanup & Hosting Guide

## 🗑️ Files to Remove (Not Required)

### Safe to Delete

These files are redundant, backup, or not needed for production:

```bash
# Navigate to whatsapp folder
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Remove backup files
rm app.py.backup
rm app.py.old

# Remove Windows-specific files (if deploying to Linux server)
rm ngrok.exe

# Remove diagnostic scripts (only needed for development debugging)
rm check_buckets.py
rm diagnose.py
rm advanced_diagnose.py

# Remove local tunneling script (not needed in production)
rm start_tunnel.py
```

### Keep These Files (Required)

✅ **Core Application Files:**
- `app.py` - Main Flask application
- `message_handler.py` - Message processing logic
- `whatsapp_service.py` - WhatsApp API integration
- `storage_service.py` - Supabase storage operations
- `modal_service.py` - Modal AI integration
- `config.py` - Configuration management
- `requirements.txt` - Python dependencies

✅ **Configuration & Data:**
- `.env` - Environment variables (create from template, don't commit)
- `.gitignore` - Git ignore rules
- `README.md` - Documentation
- `database_schema.sql` - Database setup

✅ **Documentation:**
- `docs/` folder - All documentation files

---

## 🌐 Free Hosting Options for WhatsApp Bot

### Option 1: **Render.com** (Recommended - Easiest)

**Pros:**
- ✅ Free tier available (750 hours/month)
- ✅ Automatic deployments from GitHub
- ✅ Built-in SSL
- ✅ Easy environment variable management
- ✅ Auto-restart on crashes
- ✅ Simple to use

**Cons:**
- ⚠️ Spins down after 15 minutes of inactivity (cold starts ~30s)
- ⚠️ 512MB RAM limit on free tier

**Setup Steps:**

1. **Prepare Your Code:**
   ```bash
   # Create a Procfile in whatsapp/ folder
   echo "web: gunicorn app:app" > Procfile
   
   # Ensure gunicorn is in requirements.txt (already there)
   ```

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

3. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `whatsapp-bot-deepfake`
     - **Root Directory**: `whatsapp`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Plan**: Free

4. **Add Environment Variables:**
   - In Render dashboard, go to "Environment"
   - Add all variables from `.env`:
     ```
     SUPABASE_URL=...
     SUPABASE_KEY=...
     WHATSAPP_ACCESS_TOKEN=...
     WHATSAPP_PHONE_NUMBER_ID=...
     VERIFY_TOKEN=...
     MODAL_API_URL=...
     ```

5. **Get Webhook URL:**
   - After deployment, copy your URL: `https://whatsapp-bot-deepfake.onrender.com`
   - Webhook endpoint: `https://whatsapp-bot-deepfake.onrender.com/webhook`

6. **Update WhatsApp Webhook:**
   - Go to Meta for Developers
   - Update webhook URL with your Render URL

**Cost:** FREE (with cold starts)

---

### Option 2: **Railway.app**

**Pros:**
- ✅ $5 free credit per month (enough for small usage)
- ✅ No cold starts
- ✅ Fast deployments
- ✅ Good developer experience
- ✅ Automatic HTTPS

**Cons:**
- ⚠️ Requires credit card (but still free)
- ⚠️ After $5 credit, charges apply

**Setup Steps:**

1. **Create railway.json:**
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "gunicorn app:app",
       "healthcheckPath": "/health"
     }
   }
   ```

2. **Deploy:**
   - Go to https://railway.app
   - Sign up with GitHub
   - "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Set root directory to `whatsapp/`
   - Add environment variables

3. **Get Domain:**
   - Railway provides: `your-app.railway.app`
   - Use as webhook URL

**Cost:** FREE up to $5/month usage

---

### Option 3: **Fly.io**

**Pros:**
- ✅ Generous free tier
- ✅ No cold starts
- ✅ Global edge deployment
- ✅ Good performance

**Cons:**
- ⚠️ Requires credit card
- ⚠️ CLI-based setup (more complex)

**Setup Steps:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create fly.toml:**
   ```toml
   app = "whatsapp-bot-deepfake"
   primary_region = "iad"

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     PORT = "8080"

   [[services]]
     http_checks = []
     internal_port = 8080
     protocol = "tcp"

     [[services.ports]]
       force_https = true
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443

   [deploy]
     release_command = "echo 'Deploying WhatsApp bot'"
   ```

3. **Deploy:**
   ```bash
   cd whatsapp/
   fly launch --no-deploy
   fly secrets set SUPABASE_URL=... SUPABASE_KEY=... (etc.)
   fly deploy
   ```

**Cost:** FREE for 3 shared-cpu VMs

---

### Option 4: **Heroku** (Requires Credit Card)

**Pros:**
- ✅ Very popular, lots of documentation
- ✅ Easy to use
- ✅ Good addon ecosystem

**Cons:**
- ⚠️ No longer has free tier
- ⚠️ Minimum $5/month for Eco Dynos
- ❌ Not recommended for free hosting

**Not recommended** unless you're willing to pay.

---

### Option 5: **PythonAnywhere** (Limited Free Tier)

**Pros:**
- ✅ True free tier (always-on)
- ✅ No credit card required
- ✅ Python-focused

**Cons:**
- ⚠️ Complex webhook setup
- ⚠️ Limited to HTTP only (no HTTPS on free tier)
- ❌ WhatsApp requires HTTPS, so NOT suitable

---

### Option 6: **Google Cloud Run**

**Pros:**
- ✅ Generous free tier (2 million requests/month)
- ✅ Scales to zero (no cost when idle)
- ✅ Fast cold starts
- ✅ Production-grade infrastructure

**Cons:**
- ⚠️ Requires credit card
- ⚠️ More complex setup

**Setup Steps:**

1. **Install gcloud CLI**

2. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
   ```

3. **Deploy:**
   ```bash
   gcloud run deploy whatsapp-bot \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

**Cost:** FREE for most use cases

---

## 🏆 Recommendation Summary

### Best for Beginners: **Render.com**
- Easiest setup
- No credit card needed
- Works immediately
- Accept the 15-minute cold start delay

### Best for Production: **Railway.app**
- No cold starts
- Fast and reliable
- $5 free credit/month is enough for most bots
- Requires credit card

### Best for Scale: **Google Cloud Run**
- Free tier handles millions of requests
- Production-grade
- More complex setup

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Remove unnecessary files (backups, diagnostics, ngrok.exe)
- [ ] `.env` is in `.gitignore` (don't commit secrets!)
- [ ] `gunicorn` is in `requirements.txt`
- [ ] Create `Procfile` for Render: `web: gunicorn app:app`
- [ ] Test locally: `python app.py`
- [ ] Verify all environment variables are documented
- [ ] Update `README.md` with deployment instructions
- [ ] Test webhook verification endpoint: `GET /webhook`
- [ ] Test health check endpoint: `GET /health`

---

## 🚀 Deployment Commands

### Clean Up Local Files
```bash
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Remove unnecessary files
rm -f app.py.backup app.py.old ngrok.exe
rm -f check_buckets.py diagnose.py advanced_diagnose.py start_tunnel.py

# Verify what's left
ls -la
```

### Create Procfile for Render
```bash
echo "web: gunicorn app:app --bind 0.0.0.0:\$PORT" > Procfile
```

### Test Locally
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with gunicorn (production server)
gunicorn app:app --bind 0.0.0.0:5000

# Test in another terminal
curl http://localhost:5000/health
# Should return: {"status": "healthy", "service": "whatsapp-bot-deepfake-detector"}
```

### Push to GitHub
```bash
git add .
git commit -m "Prepare WhatsApp bot for deployment"
git push origin main
```

---

## 🔧 Environment Variables Template

Create this as `.env.example` for documentation:

```env
# WhatsApp Business API
VERIFY_TOKEN=your_custom_verify_token_here
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# Modal AI (Image Detection)
MODAL_API_URL=https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
# MODAL_API_KEY=optional_if_secured

# Flask (optional)
FLASK_ENV=production
```

---

## 📊 Hosting Comparison Table

| Feature | Render | Railway | Fly.io | Cloud Run | Heroku |
|---------|--------|---------|--------|-----------|--------|
| **Free Tier** | ✅ Yes | ✅ $5 credit | ✅ Yes | ✅ Yes | ❌ No |
| **Credit Card** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cold Starts** | ⚠️ Yes (15min) | ✅ No | ✅ No | ⚠️ Yes (fast) | N/A |
| **Auto Deploy** | ✅ GitHub | ✅ GitHub | ⚠️ CLI | ⚠️ CLI | ✅ GitHub |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Reliability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 Final Recommendation

**For your WhatsApp bot, I recommend: Render.com**

### Why?
1. **No credit card required** - Start immediately
2. **Easy GitHub integration** - Push to deploy
3. **Free forever** - No time limit
4. **HTTPS included** - Required for WhatsApp webhooks
5. **Simple environment variables** - Easy configuration

### Accept This Trade-off:
- 15-minute cold starts are acceptable for a WhatsApp bot
- Users won't notice since WhatsApp messages are asynchronous
- First message after idle takes ~30s, subsequent messages are instant

### Next Steps:
1. Clean up unnecessary files (run commands above)
2. Create Procfile
3. Push to GitHub
4. Deploy to Render.com
5. Update WhatsApp webhook URL
6. Test with a message!

---

**Good luck with deployment! 🚀**

