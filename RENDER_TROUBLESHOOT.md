# Render Deployment - Modal Not Working Fix

## Problem
Images upload successfully but Modal AI detection doesn't run - you get "uploaded successfully" message instead of AI results.

## Most Likely Cause
**MODAL_API_URL environment variable is missing on Render!**

---

## Fix: Add MODAL_API_URL to Render

### Step 1: Go to Render Dashboard
https://dashboard.render.com

### Step 2: Click on Your Web Service
Click on `whatsapp-bot` (or whatever you named it)

### Step 3: Go to Environment Tab
Click **"Environment"** in the left sidebar

### Step 4: Add MODAL_API_URL
Click **"Add Environment Variable"**

```
Key: MODAL_API_URL
Value: https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
```

Click **"Save Changes"**

### Step 5: Wait for Redeploy
Render will automatically redeploy (takes ~2 minutes)

### Step 6: Test Again
Send an image to your WhatsApp bot - should now show AI detection results!

---

## Check Render Logs

To see what's happening:

1. In Render dashboard, click your service
2. Click **"Logs"** tab
3. Send an image to your bot
4. Look for these lines:
   ```
   🤖 Running AI detection on image...
   🔗 Modal API URL: https://...
   ✅ AI detection complete: ...
   ```

If you see:
```
🔗 Modal API URL: NOT SET
```
Then MODAL_API_URL is missing - go back to Step 4!

---

## All Environment Variables Needed

Make sure ALL these are set in Render:

```
VERIFY_TOKEN=abc123
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_id
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
MODAL_API_URL=https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
```

---

## Still Not Working?

### Check Modal API is Running

Test Modal directly:
```bash
curl https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run/health
```

Should return:
```json
{"status":"healthy","device":"cuda","cuda_available":true,"model_loaded":true}
```

If this fails, your Modal app is down - redeploy it.

---

## Quick Fix Summary

1. ✅ Add `MODAL_API_URL` to Render environment variables
2. ✅ Wait for redeploy
3. ✅ Test with image
4. ✅ Check logs if still not working

**Most common issue: Forgot to add MODAL_API_URL!**

