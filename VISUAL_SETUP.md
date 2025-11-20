# 🖥️ WhatsApp Bot - Visual Setup Guide

## 📺 Your Screen Layout

```
┌──────────────────────────────────────────────────────────────┐
│                      YOUR IDE (e.g., VS Code)                │
├──────────────────────────────────────────────────────────────┤
│  Files Open:                                                 │
│  ├── app.py                    [Main application]            │
│  ├── message_handler.py        [Message processing]          │
│  ├── modal_service.py          [AI detection]                │
│  ├── .env                      [Environment vars]            │
│  └── RUNNING_LOCALLY.md        [This guide]                  │
├──────────────────────────────────────────────────────────────┤
│  Terminal 1: Flask App                                       │
│  $ cd whatsapp/                                              │
│  $ source venv/bin/activate                                  │
│  $ python app.py                                             │
│  ✅ Running on http://0.0.0.0:5000                          │
│  [KEEP THIS OPEN - DON'T CLOSE]                             │
├──────────────────────────────────────────────────────────────┤
│  Terminal 2: ngrok Tunnel                                    │
│  $ cd whatsapp/                                              │
│  $ ./ngrok.exe http 5000                                     │
│  ✅ Forwarding: https://abc123.ngrok.io -> localhost:5000   │
│  [KEEP THIS OPEN - DON'T CLOSE]                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔄 The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR LOCAL MACHINE                           │
│                                                                 │
│  ┌────────────────────┐         ┌──────────────────┐          │
│  │  Terminal 1        │         │  Terminal 2       │          │
│  │                    │         │                   │          │
│  │  python app.py     │◄────────┤  ngrok.exe        │          │
│  │                    │         │                   │          │
│  │  Flask Server      │         │  Public Tunnel    │          │
│  │  localhost:5000    │         │  abc123.ngrok.io  │          │
│  └────────────────────┘         └──────────────────┘          │
│           ▲                              │                      │
│           │                              │                      │
│           │                              ▼                      │
│           │                    ┌──────────────────┐            │
│           │                    │   INTERNET       │            │
│           │                    └──────────────────┘            │
│           │                              │                      │
│           │                              ▼                      │
│           │                    ┌──────────────────┐            │
│           └────────────────────┤ WhatsApp Cloud   │            │
│                                │ API              │            │
│                                └──────────────────┘            │
│                                         │                       │
│                                         ▼                       │
│                                ┌──────────────────┐            │
│                                │ User's WhatsApp  │            │
│                                │ Mobile App       │            │
│                                └──────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Message Flow Example

### 1. User Sends Image

```
User's Phone                     WhatsApp Cloud API
    │                                   │
    │ [Sends "hi"]                      │
    ├──────────────────────────────────►│
    │                                   │
    │                                   │  POST /webhook
    │                                   ├──────────────►
    │                                   │         Your Flask App
    │                                   │         (Terminal 1)
    │                                   │              │
    │  [Receives welcome message]       │              │ Process message
    │◄──────────────────────────────────┤              │ Send response
    │                                   │◄─────────────┤
    │                                   │
    │ [Sends "1" for image]             │
    ├──────────────────────────────────►│
    │                                   │  POST /webhook
    │                                   ├──────────────►
    │                                   │         Your Flask App
    │  [Receives "Send image"]          │              │
    │◄──────────────────────────────────┤              │
    │                                   │◄─────────────┤
    │                                   │
    │ [Uploads image]                   │
    ├──────────────────────────────────►│
    │                                   │  POST /webhook (with media_id)
    │                                   ├──────────────►
    │                                   │         Your Flask App
    │                                   │              │
    │                                   │         1. Download image
    │                                   │         2. Upload to Supabase
    │                                   │         3. Call Modal AI ──┐
    │                                   │              │             │
    │                                   │              │◄────────────┘
    │                                   │         4. Save to DB
    │                                   │         5. Format response
    │  [Receives AI detection result]   │              │
    │◄──────────────────────────────────┤◄─────────────┤
    │                                   │
```

---

## 🎬 Step-by-Step Visual

### Step 1: Open IDE and Navigate
```
📂 /home/lightdesk/Projects/AI-Website/whatsapp/
  ├── 📄 app.py              ← OPEN THIS
  ├── 📄 message_handler.py  ← OPEN THIS
  ├── 📄 modal_service.py    ← OPEN THIS
  ├── 📄 .env                ← OPEN THIS
  ├── 📄 requirements.txt
  └── 📁 venv/
```

### Step 2: Terminal 1 - Start Flask
```
┌────────────────────────────────────────────────┐
│ Terminal 1                                     │
├────────────────────────────────────────────────┤
│ $ cd /home/lightdesk/Projects/AI-Website/     │
│   whatsapp                                     │
│ $ source venv/bin/activate                     │
│ (venv) $ python app.py                         │
│                                                │
│ 🚀 Starting WhatsApp Deepfake Detector Bot... │
│ 📱 Webhook endpoint: /webhook                  │
│ 🌐 API endpoints: /api/*                       │
│ 💚 Health check: /health                       │
│  * Running on http://0.0.0.0:5000             │
│  * Debug mode: on                              │
│                                                │
│ ✅ READY - LEAVE THIS RUNNING                 │
└────────────────────────────────────────────────┘
```

### Step 3: Terminal 2 - Start ngrok
```
┌────────────────────────────────────────────────┐
│ Terminal 2                                     │
├────────────────────────────────────────────────┤
│ $ cd /home/lightdesk/Projects/AI-Website/     │
│   whatsapp                                     │
│ $ ./ngrok.exe http 5000                        │
│                                                │
│ ngrok                                          │
│                                                │
│ Session Status    online                       │
│ Account           Your Account                 │
│ Version           3.x.x                        │
│ Region            United States (us)           │
│ Latency           45ms                         │
│ Web Interface     http://127.0.0.1:4040       │
│ Forwarding        https://abc123.ngrok.io ->  │
│                   http://localhost:5000        │
│                                                │
│ ✅ COPY THIS URL: https://abc123.ngrok.io     │
│ ✅ LEAVE THIS RUNNING                          │
└────────────────────────────────────────────────┘
```

### Step 4: Configure WhatsApp Webhook
```
┌────────────────────────────────────────────────┐
│ Meta Developer Console                         │
│ https://developers.facebook.com/               │
├────────────────────────────────────────────────┤
│ WhatsApp > Configuration > Webhook             │
│                                                │
│ Callback URL:                                  │
│ ┌──────────────────────────────────────────┐  │
│ │ https://abc123.ngrok.io/webhook          │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ Verify Token:                                  │
│ ┌──────────────────────────────────────────┐  │
│ │ abc123 (from your .env file)             │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ [Verify and Save] ← Click this                 │
│                                                │
│ Subscribe to:                                  │
│ ☑ messages                                     │
│                                                │
│ [Subscribe] ← Click this                       │
└────────────────────────────────────────────────┘
```

---

## 💬 Testing - What You'll See

### On Your Phone (WhatsApp):
```
┌──────────────────────────────────┐
│  WhatsApp Chat                   │
├──────────────────────────────────┤
│  You: hi                         │
│                                  │
│  Bot:                            │
│  👋 Hey there! Welcome to        │
│  *Deepfake Detector Bot*!        │
│                                  │
│  Please choose what you'd        │
│  like to analyze:                │
│                                  │
│  1️⃣ Send *1* for Image 🖼      │
│  2️⃣ Send *2* for Video 🎥      │
│  3️⃣ Send *3* for Text 📝       │
│                                  │
│  You: 1                          │
│                                  │
│  Bot:                            │
│  🖼 Great! Please send me an    │
│  *image* that you want to        │
│  analyze for deepfakes.          │
│                                  │
│  You: [Uploads image]            │
│                                  │
│  Bot:                            │
│  ✅ *Detection Results*          │
│                                  │
│  📁 File: image_123.jpg          │
│  🤖 Model: EfficientFormer-S2V1  │
│                                  │
│  ✅ *Authentic Human Content*    │
│                                  │
│  📊 *Confidence Score*           │
│  🟢 92% ██████████              │
│                                  │
│  💡 Type *start* to analyze      │
│  another file!                   │
└──────────────────────────────────┘
```

### In Terminal 1 (Flask Logs):
```
Webhook received: {'entry': [...]
📤 Uploading to bucket: image-uploads
✅ Upload response: {...}
🔗 Public URL generated: https://...supabase.co/...
🤖 Running AI detection on image...
✅ AI detection complete: Authentic Human Content (92%)
💾 Storing metadata in detection_history table...
✅ Metadata stored successfully! Record ID: abc-123
Message sent to +1234567890: {...}
```

### In Terminal 2 (ngrok Dashboard):
```
HTTP Requests
-------------
POST /webhook    200 OK    152ms
POST /webhook    200 OK    3.2s   (AI detection takes longer)
GET  /health     200 OK    12ms
```

---

## 🎯 Checklist While Running

```
Before Sending Messages:
[ ] Terminal 1 shows: "Running on http://0.0.0.0:5000" ✅
[ ] Terminal 2 shows: "Forwarding https://...ngrok.io" ✅
[ ] Webhook URL updated in Meta console ✅
[ ] "messages" subscribed in webhook settings ✅

When Message Received:
[ ] Terminal 1 shows: "Webhook received" ✅
[ ] Terminal 1 shows: "🤖 Running AI detection" (for images) ✅
[ ] Terminal 1 shows: "✅ AI detection complete" ✅
[ ] Phone receives response message ✅

If Something Goes Wrong:
[ ] Check Terminal 1 for errors (Flask logs)
[ ] Check Terminal 2 for connection issues
[ ] Visit http://127.0.0.1:4040 for ngrok dashboard
[ ] Verify .env variables are correct
[ ] Test: curl http://localhost:5000/health
```

---

## 🔧 Common Console Errors & Fixes

### Error in Terminal 1:
```
❌ ModuleNotFoundError: No module named 'flask'
```
**Fix**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Error in Terminal 1:
```
❌ Error: SUPABASE_URL must be set in environment variables
```
**Fix**: Check `.env` file exists and has all variables

---

### Error in Terminal 2:
```
❌ ngrok.exe: command not found
```
**Fix**: 
```bash
# Make sure you're in the whatsapp folder
cd /home/lightdesk/Projects/AI-Website/whatsapp
ls ngrok.exe  # Should exist
./ngrok.exe http 5000
```

---

### No Logs in Terminal 1:
```
(Nothing happens when you send WhatsApp message)
```
**Fix**:
1. Check ngrok is running (Terminal 2)
2. Check webhook URL is correct in Meta console
3. Check "messages" is subscribed
4. Try sending "hi" again

---

## 🎉 Success Indicators

### ✅ Everything Working When You See:

**Terminal 1**:
- Shows: `Running on http://0.0.0.0:5000`
- Shows: `Webhook received` when you send messages
- Shows: `🤖 Running AI detection` for images
- Shows: `Message sent to +123...` after processing

**Terminal 2**:
- Shows: `Forwarding https://...ngrok.io -> http://localhost:5000`
- Shows: `POST /webhook 200 OK` for each message

**Your Phone**:
- Receives welcome message
- Receives "Send image" message after "1"
- Receives AI detection results after uploading image

**Supabase Dashboard**:
- New row in `detection_history` table
- Image file in `image-uploads` bucket

---

## 📚 Quick Links

- **Complete Guide**: `RUNNING_LOCALLY.md`
- **Quick Reference**: `QUICK_START.md`
- **Deployment**: `CLEANUP_AND_HOSTING.md`
- **ngrok Dashboard**: http://127.0.0.1:4040 (when running)

---

**You're all set! Happy bot running! 🚀📱🤖**

