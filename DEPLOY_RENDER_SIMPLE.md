# Deploy WhatsApp Bot to Render - Simple Steps

**No ngrok needed!** Render gives you a free public URL.

---

## Step 1: Push to GitHub

```bash
cd /home/lightdesk/Projects/AI-Website/whatsapp
git add .
git commit -m "Deploy WhatsApp bot"
git push origin main
```

---

## Step 2: Sign Up on Render

Go to: https://render.com  
Click "Get Started" → Sign up with GitHub

---

## Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** → Select your repository
3. Configure:
   - **Name**: `whatsapp-bot`
   - **Root Directory**: `whatsapp`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. Click **"Create Web Service"**

---

## Step 4: Add Environment Variables

In Render dashboard, go to **"Environment"** tab:

```
VERIFY_TOKEN=abc123
WHATSAPP_ACCESS_TOKEN=your_token_from_meta
WHATSAPP_PHONE_NUMBER_ID=your_id_from_meta
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
MODAL_API_URL=https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
```

Click **"Save Changes"**

---

## Step 5: Get Your URL

After deployment completes:
- Copy your URL: `https://whatsapp-bot.onrender.com`
- This is your **permanent public URL** ✅

---

## Step 6: Update WhatsApp Webhook

1. Go to: https://developers.facebook.com
2. Select your WhatsApp app
3. Go to **WhatsApp** → **Configuration**
4. Click **"Edit"** on Webhook
5. Enter:
   - **Callback URL**: `https://whatsapp-bot.onrender.com/webhook`
   - **Verify Token**: `abc123` (same as your VERIFY_TOKEN)
6. Click **"Verify and Save"**
7. Check **"messages"** subscription

---

## Step 7: Test

Send "hi" to your WhatsApp bot!

---

## Done! 🎉

Your bot is live 24/7 with a permanent URL.  
**No ngrok needed!**

---

## Important Notes

- First request may be slow (cold start ~30s)
- After 15 min idle, bot sleeps (free tier)
- Subsequent requests are fast
- URL never changes ✅

