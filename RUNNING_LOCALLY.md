# 🚀 Running WhatsApp Bot Locally - Complete Guide

## ⚡ Quick Answer

**Yes, you need TWO programs running simultaneously:**

1. **Flask App** (`python app.py`) - Your WhatsApp bot server
2. **ngrok/Grok** - Tunnel to expose your local server to the internet

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [x] Python 3.8+ installed
- [x] Virtual environment created
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file configured with all credentials
- [x] Supabase buckets created (`image-uploads`, `video-uploads`, `text-uploads`)
- [x] Supabase database table `detection_history` created
- [x] WhatsApp Business API access (Meta Developer account)
- [x] ngrok or Grok account (for tunneling)

---

## 🗂️ Files to Have Open in Your IDE

### Essential Files (Open These):

1. **`app.py`** - Main application (check for errors)
2. **`message_handler.py`** - Message processing logic
3. **`.env`** - Environment variables (verify all are set)
4. **Terminal 1** - For running Flask app
5. **Terminal 2** - For running ngrok/Grok tunnel

### Reference Files (Keep handy):

6. **`modal_service.py`** - AI detection (check if Modal is working)
7. **`config.py`** - Configuration (verify settings)
8. **`docs/MODAL_INTEGRATION.md`** - Reference guide

---

## 🎯 Step-by-Step Running Instructions

### Step 1: Verify Environment Setup

```bash
# Navigate to whatsapp folder
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Check if .env exists
ls -la .env

# Verify Python version
python --version  # Should be 3.8 or higher
```

### Step 2: Activate Virtual Environment

```bash
# Activate virtual environment
source venv/bin/activate

# On Windows (if needed):
# venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
```

### Step 3: Verify Dependencies

```bash
# Install/update dependencies
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "Flask|supabase|requests|gunicorn"
```

### Step 4: Check Environment Variables

```bash
# Display environment variables (without showing actual values)
cat .env | grep -v "^#" | sed 's/=.*/=***/'

# Required variables:
# VERIFY_TOKEN=***
# WHATSAPP_ACCESS_TOKEN=***
# WHATSAPP_PHONE_NUMBER_ID=***
# SUPABASE_URL=***
# SUPABASE_KEY=***
# MODAL_API_URL=***
```

### Step 5: Test Modal API Connection (Optional but Recommended)

```bash
# Test if Modal API is reachable
python modal_service.py

# Expected output:
# 🧪 Testing Modal API connection...
# Health check: ✅ Modal API is healthy (Device: cuda, CUDA: True)
```

---

## 🚀 Running the Bot - TWO TERMINAL SETUP

### Terminal 1: Flask App

```bash
# Navigate to whatsapp folder
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Activate virtual environment
source venv/bin/activate

# Run Flask app
python app.py

# Expected output:
# 🚀 Starting WhatsApp Deepfake Detector Bot...
# 📱 Webhook endpoint: /webhook
# 🌐 API endpoints: /api/*
# 💚 Health check: /health
#  * Running on http://0.0.0.0:5000
#  * Debug mode: on
```

**Keep this terminal running!** ✅

---

### Terminal 2: ngrok/Grok Tunnel

You have two options:

#### Option A: Using ngrok (Windows - ngrok.exe)

```bash
# In the same whatsapp folder (separate terminal)
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Run ngrok (Windows)
ngrok.exe http 5000

# Expected output:
# Session Status: online
# Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

#### Option B: Using Grok (if you have it)

```bash
# Install grok if not installed
npm install -g @cloudflare/grok

# Run grok tunnel
grok tunnel http://localhost:5000

# Get your public URL
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`) - you'll need this!

**Keep this terminal running!** ✅

---

## 🔗 Configure WhatsApp Webhook

### Step 1: Copy Your Tunnel URL

From Terminal 2, copy the HTTPS URL:
```
https://abc123.ngrok.io  # Example ngrok URL
```

### Step 2: Update Meta Developer Console

1. Go to https://developers.facebook.com/
2. Select your app
3. Go to **WhatsApp** → **Configuration**
4. Click **Edit** on Webhook
5. Enter:
   - **Callback URL**: `https://abc123.ngrok.io/webhook`
   - **Verify Token**: (same as `VERIFY_TOKEN` in your `.env`)
6. Click **Verify and Save**

### Step 3: Subscribe to Webhooks

Still in Meta Developer Console:
- Check the box for **messages**
- Click **Subscribe**

---

## ✅ Verification Steps

### 1. Test Health Endpoint

```bash
# In a third terminal or browser
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","service":"whatsapp-bot-deepfake-detector"}
```

### 2. Test Webhook Verification

```bash
# Replace YOUR_TOKEN with your actual VERIFY_TOKEN
curl "http://localhost:5000/webhook?hub.verify_token=YOUR_TOKEN&hub.challenge=TEST"

# Expected response:
# TEST
```

### 3. Test with WhatsApp

1. **Send a text message** to your WhatsApp number:
   ```
   hi
   ```
   Expected: Welcome message with options

2. **Send "1"**:
   Expected: "Great! Please send me an image..."

3. **Send an image**:
   Expected: Detailed AI detection results

---

## 🖥️ Visual Setup

```
┌─────────────────────────────────┐
│  Terminal 1: Flask App          │
│  $ python app.py                │
│  Running on http://0.0.0.0:5000 │
│  [Keep Running] ✅              │
└─────────────────────────────────┘
              ↓
         (localhost)
              ↓
┌─────────────────────────────────┐
│  Terminal 2: ngrok Tunnel       │
│  $ ngrok.exe http 5000          │
│  https://abc123.ngrok.io        │
│  [Keep Running] ✅              │
└─────────────────────────────────┘
              ↓
         (internet)
              ↓
┌─────────────────────────────────┐
│  WhatsApp Cloud API             │
│  Sends messages to your webhook │
└─────────────────────────────────┘
```

---

## 📝 Typical Console Output

### Terminal 1 (Flask) - Expected Output:

```
🚀 Starting WhatsApp Deepfake Detector Bot...
📱 Webhook endpoint: /webhook
🌐 API endpoints: /api/*
💚 Health check: /health
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.x:5000

Webhook verified successfully

Webhook received: {'entry': [...]}
📤 Uploading to bucket: image-uploads, filename: 1234567890_image.jpg
✅ Upload response: {...}
🔗 Public URL generated: https://...
🤖 Running AI detection on image...
✅ AI detection complete: Authentic Human Content (92%)
💾 Storing metadata in detection_history table...
✅ Metadata stored successfully! Record ID: abc-123
Message sent to +1234567890: {...}
```

### Terminal 2 (ngrok) - Expected Output:

```
ngrok

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              142     1       0.00    0.01    24.32   98.33

HTTP Requests
-------------

POST /webhook                  200 OK
POST /webhook                  200 OK
GET  /health                   200 OK
```

---

## 🛠️ Troubleshooting

### Problem 1: Flask App Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate virtual environment first!
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

### Problem 2: ngrok Won't Start

**Error**: `ngrok.exe: command not found`

**Solution**:
```bash
# Make sure you're in the whatsapp folder
cd /home/lightdesk/Projects/AI-Website/whatsapp

# Run with explicit path
./ngrok.exe http 5000

# Or on Windows Command Prompt:
ngrok.exe http 5000
```

---

### Problem 3: Webhook Verification Failed

**Error**: "Verification failed" in Meta Developer Console

**Solutions**:
1. Check `VERIFY_TOKEN` in `.env` matches what you entered in Meta console
2. Ensure ngrok is running and URL is correct
3. Try the verification URL manually:
   ```bash
   curl "https://YOUR_NGROK_URL/webhook?hub.verify_token=YOUR_TOKEN&hub.challenge=TEST"
   ```

---

### Problem 4: Messages Not Received

**Checklist**:
- [ ] Flask app is running (Terminal 1)
- [ ] ngrok is running (Terminal 2)
- [ ] Webhook URL is updated in Meta Developer Console
- [ ] "messages" is subscribed in webhook settings
- [ ] Phone number is verified in WhatsApp Business API

**Debug**:
```bash
# Check Flask logs in Terminal 1
# Should see "Webhook received: {...}" when you send a message
```

---

### Problem 5: Modal AI Detection Fails

**Error**: "Modal API detection failed" in console

**Solution**:
```bash
# Test Modal API
python modal_service.py

# If health check fails:
# 1. Check MODAL_API_URL in .env
# 2. Verify Modal app is deployed and running
# 3. Check Modal dashboard: https://modal.com/apps
```

---

## 🔄 Restart Process

If you need to restart:

### Stop Both Terminals:
```bash
# Terminal 1 (Flask): Press Ctrl+C
# Terminal 2 (ngrok): Press Ctrl+C
```

### Start Again:
```bash
# Terminal 1:
cd /home/lightdesk/Projects/AI-Website/whatsapp
source venv/bin/activate
python app.py

# Terminal 2:
cd /home/lightdesk/Projects/AI-Website/whatsapp
./ngrok.exe http 5000
```

**Note**: ngrok URL changes each time you restart (on free plan), so you'll need to update the webhook URL in Meta Developer Console again!

---

## 💡 Pro Tips

### 1. Keep ngrok URL Stable (Free Plan)

On free ngrok plan, URL changes on restart. To avoid updating Meta console every time:

**Option A**: Upgrade to ngrok Pro ($8/month) for permanent URL

**Option B**: Deploy to production (Render.com is free and gives permanent URL)

### 2. Monitor Logs

Keep Terminal 1 (Flask) visible to see:
- Incoming messages
- File uploads
- AI detection results
- Errors

### 3. Use ngrok Dashboard

Open in browser: http://127.0.0.1:4040
- See all requests
- Inspect request/response
- Debug webhook issues

### 4. Test Health Endpoint

```bash
# Quick test if bot is working
curl http://localhost:5000/health
```

---

## 📊 Checklist Before Running

```
Prerequisites:
[ ] Python 3.8+ installed
[ ] Virtual environment created (venv/)
[ ] Dependencies installed (requirements.txt)
[ ] .env file configured with all variables
[ ] Supabase buckets created
[ ] Supabase table created
[ ] WhatsApp Business API access
[ ] ngrok.exe or similar tunnel tool

Files Open in IDE:
[ ] app.py
[ ] message_handler.py
[ ] .env
[ ] Terminal 1 (for Flask)
[ ] Terminal 2 (for ngrok)

Running:
[ ] Terminal 1: python app.py (RUNNING ✅)
[ ] Terminal 2: ngrok.exe http 5000 (RUNNING ✅)
[ ] Health check: curl localhost:5000/health (WORKS ✅)
[ ] Webhook configured in Meta console (DONE ✅)
[ ] Test message sent to WhatsApp (SUCCESS ✅)
```

---

## 🎯 Quick Start Commands

### Complete Startup Sequence:

```bash
# Terminal 1 - Flask App
cd /home/lightdesk/Projects/AI-Website/whatsapp
source venv/bin/activate
python app.py

# Terminal 2 - ngrok (in separate terminal window)
cd /home/lightdesk/Projects/AI-Website/whatsapp
./ngrok.exe http 5000

# Then:
# 1. Copy ngrok HTTPS URL from Terminal 2
# 2. Update webhook in Meta Developer Console
# 3. Send test message to WhatsApp
# 4. Watch Terminal 1 for logs
```

---

## 🎉 You're Ready!

When both terminals show:
- **Terminal 1**: `Running on http://0.0.0.0:5000` ✅
- **Terminal 2**: `Forwarding https://xxx.ngrok.io -> http://localhost:5000` ✅

Your WhatsApp bot is **LIVE** and ready to receive messages! 🚀

Send "hi" to your WhatsApp number to test!

---

**Need Help?**
- Check Terminal 1 for Flask errors
- Check Terminal 2 for ngrok connection issues  
- Visit ngrok dashboard: http://127.0.0.1:4040
- Check Meta Developer Console for webhook errors

**Happy Bot Running! 🤖📱**

