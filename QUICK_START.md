# ⚡ WhatsApp Bot - Quick Start Reference

## 🎯 Two Programs Required

| Terminal | Program | Command |
|----------|---------|---------|
| **Terminal 1** | Flask App | `python app.py` |
| **Terminal 2** | ngrok Tunnel | `./ngrok.exe http 5000` |

**Both must be running simultaneously!**

---

## 🚀 Quick Start (3 Steps)

### 1. Terminal 1 - Start Flask App
```bash
cd /home/lightdesk/Projects/AI-Website/whatsapp
source venv/bin/activate
python app.py
```
✅ Leave running - should show: `Running on http://0.0.0.0:5000`

### 2. Terminal 2 - Start ngrok
```bash
cd /home/lightdesk/Projects/AI-Website/whatsapp
./ngrok.exe http 5000
```
✅ Leave running - copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 3. Update WhatsApp Webhook
- Go to https://developers.facebook.com/
- Update webhook URL: `https://abc123.ngrok.io/webhook`
- Verify token matches your `.env` file

**Done! Send "hi" to your WhatsApp bot to test!** 🎉

---

## 📁 Files to Open in IDE

Essential:
1. **app.py** - Main application
2. **message_handler.py** - Message logic
3. **.env** - Environment variables
4. **Terminal 1** - Flask logs
5. **Terminal 2** - ngrok status

---

## ✅ Quick Tests

### Test 1: Health Check
```bash
curl http://localhost:5000/health
```
Expected: `{"status":"healthy",...}`

### Test 2: Webhook Verification
```bash
curl "http://localhost:5000/webhook?hub.verify_token=YOUR_TOKEN&hub.challenge=TEST"
```
Expected: `TEST`

### Test 3: WhatsApp Message
Send to bot: `hi`  
Expected: Welcome message

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `Module not found` | Run: `pip install -r requirements.txt` |
| `ngrok not found` | Check you're in `whatsapp/` folder |
| No messages received | Check both terminals are running |
| Webhook verification fails | Check `VERIFY_TOKEN` in `.env` |
| AI detection fails | Test: `python modal_service.py` |

---

## 🔄 Restart Commands

Stop: Press `Ctrl+C` in both terminals

Start again:
```bash
# Terminal 1
python app.py

# Terminal 2
./ngrok.exe http 5000
```

**Note**: ngrok URL changes on restart (free plan) - update Meta console!

---

## 📊 Expected Console Output

### Terminal 1 (Flask):
```
🚀 Starting WhatsApp Deepfake Detector Bot...
📱 Webhook endpoint: /webhook
💚 Health check: /health
 * Running on http://0.0.0.0:5000
```

### Terminal 2 (ngrok):
```
Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

---

## 💡 Quick Reference

### Environment Variables (.env):
```env
VERIFY_TOKEN=abc123
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_id
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
MODAL_API_URL=https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
```

### WhatsApp Commands:
- Send `hi` - Welcome message
- Send `1` - Image mode
- Send `2` - Video mode  
- Send `3` - Text mode
- Send image after `1` - Get AI detection

---

## 📚 Full Documentation

- **Complete Guide**: `RUNNING_LOCALLY.md`
- **Deployment**: `CLEANUP_AND_HOSTING.md`
- **Integration**: `docs/MODAL_INTEGRATION.md`

---

**Ready to go! 🚀**

