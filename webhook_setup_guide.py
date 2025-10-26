#!/usr/bin/env python3
"""
Step-by-step Webhook Configuration Guide for WhatsApp Bot
Run this to see your current ngrok URL and configuration details
"""
import subprocess
import json
import requests

print("=" * 70)
print("📋 WEBHOOK CONFIGURATION GUIDE FOR WHATSAPP")
print("=" * 70)

# Step 1: Get ngrok URL
print("\n🔍 Step 1: Finding your ngrok tunnel URL...")
print("-" * 70)

try:
    # Try to get ngrok tunnels via API
    response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
    tunnels = response.json()
    
    if tunnels.get("tunnels"):
        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
                print(f"✅ Ngrok HTTPS URL found: {ngrok_url}")
                print(f"   Forwarding to: {tunnel['config']['addr']}")
                break
    else:
        print("⚠️  No active ngrok tunnels found")
        print("   Make sure ngrok is running: ngrok http 5000")
        ngrok_url = "https://YOUR-NGROK-URL.ngrok.io"
except:
    print("⚠️  Cannot detect ngrok URL automatically")
    print("   Make sure ngrok is running in another terminal")
    ngrok_url = "https://YOUR-NGROK-URL.ngrok.io"

webhook_url = f"{ngrok_url}/webhook"

print("\n" + "=" * 70)
print("📝 WEBHOOK CONFIGURATION STEPS")
print("=" * 70)

print("""
Step 1: OPEN META DEVELOPER CONSOLE
────────────────────────────────────────────────────────────────────
1. Go to: https://developers.facebook.com/apps/
2. Log in with your Facebook account
3. Click on your WhatsApp app

Step 2: NAVIGATE TO WHATSAPP CONFIGURATION
────────────────────────────────────────────────────────────────────
1. In the left sidebar, find "WhatsApp"
2. Click on "Configuration" (or "Webhook Configuration")
   
   Alternative path:
   - If you see "Getting Started", go there first
   - Then find "Configuration" in the submenu

Step 3: CONFIGURE THE WEBHOOK
────────────────────────────────────────────────────────────────────
You'll see a section called "Webhook" or "Callback URL"

1. Click the "Edit" button next to "Callback URL"

2. Enter your webhook details:
""")

print(f"   📌 Callback URL: {webhook_url}")
print(f"   🔑 Verify Token: abc123")

print("""
3. Click "Verify and Save"

   ⚠️ IMPORTANT: Meta will send a verification request to your URL
   Your bot MUST be running for this to work!

4. If verification succeeds, you'll see a green checkmark ✓

5. If verification fails, check:
   - Is your Flask app running?
   - Is ngrok running?
   - Does the ngrok URL match what you entered?
   - Is the verify token exactly "abc123"?

Step 4: SUBSCRIBE TO WEBHOOK FIELDS
────────────────────────────────────────────────────────────────────
Below the webhook URL, you'll see "Webhook fields" section

1. Find the checkbox for "messages"
2. Make sure it's CHECKED/SUBSCRIBED (should show as subscribed)
3. This tells WhatsApp to send message events to your webhook

Other useful fields (optional):
   □ message_template_status_update
   □ phone_number_quality_update
   □ account_update

Step 5: ADD TEST PHONE NUMBER
────────────────────────────────────────────────────────────────────
1. Go to "WhatsApp" → "API Setup" in the left sidebar
2. Scroll to the "Send and receive messages" section
3. Under "To" field, click "Manage phone number list"
4. Click "Add phone number"
5. Enter your phone number with country code (e.g., +1234567890)
6. WhatsApp will send you a verification code
7. Enter the code to verify

Step 6: GET YOUR BUSINESS PHONE NUMBER
────────────────────────────────────────────────────────────────────
1. In the same "API Setup" page
2. Look for "From" field
3. You'll see your WhatsApp Business phone number
4. This is the number people should message to reach your bot!

   Example: +1 555 123 4567

Step 7: TEST YOUR BOT
────────────────────────────────────────────────────────────────────
1. Open WhatsApp on your phone
2. Start a new chat with your BUSINESS NUMBER (from Step 6)
3. Send a message like "hi" or "hello"
4. Your bot should reply with a welcome message! 🎉

Step 8: MONITOR WEBHOOK ACTIVITY
────────────────────────────────────────────────────────────────────
Watch your Flask app terminal for logs:
   - You should see "Webhook received: {...}" when messages arrive
   - You should see "Message sent to ..." when bot replies
   - Any errors will be printed here

In Meta Developer Console:
   - Go to "WhatsApp" → "Configuration"
   - You can see "Recent webhook requests" or test webhook
   - Click "Test" to send a test payload

""")

print("=" * 70)
print("🔗 QUICK REFERENCE")
print("=" * 70)
print(f"""
Your Configuration:
   Webhook URL:    {webhook_url}
   Verify Token:   abc123
   Phone Number ID: 883706248149866

Important URLs:
   Meta Developer Console: https://developers.facebook.com/apps/
   Ngrok Dashboard: http://localhost:4040 (when ngrok is running)
   Bot Health Check: http://localhost:5000/health
   
Terminal Commands:
   Start Bot:   /home/lightdesk/Projects/whatsapp/venv/bin/python app.py
   Start Ngrok: ngrok http 5000
   Check Logs:  (Watch the Flask app terminal)
   Diagnose:    /home/lightdesk/Projects/whatsapp/venv/bin/python diagnose.py
""")

print("=" * 70)
print("🐛 COMMON ISSUES")
print("=" * 70)
print("""
❌ "Webhook verification failed"
   → Make sure Flask app is running
   → Check ngrok URL is correct and active
   → Verify token must be exactly "abc123"

❌ "Messages not being received"
   → Check webhook is verified (green checkmark)
   → Make sure "messages" field is subscribed
   → Verify your phone is added to test recipients
   → Check Flask app logs for incoming webhooks

❌ "API access blocked"
   → Your access token may be expired
   → Get new token from WhatsApp → API Setup
   → Update .env file with new token
   → Restart Flask app

❌ Ngrok URL keeps changing
   → Free ngrok URLs expire every 2 hours
   → You'll need to update webhook URL in Meta Console
   → Consider ngrok paid plan for static URLs
   → Or use a cloud deployment (Heroku, Railway, etc.)
""")

print("=" * 70)
print("✅ VERIFICATION CHECKLIST")
print("=" * 70)
print("""
Before testing, make sure:
   □ Flask app is running (check http://localhost:5000/health)
   □ Ngrok is running (check http://localhost:4040)
   □ Webhook is configured in Meta Console with your ngrok URL
   □ Webhook is verified (green checkmark in Meta Console)
   □ "messages" field is subscribed
   □ Your phone number is added as test recipient
   □ You have a fresh access token (not expired)
   □ You know your WhatsApp Business phone number
   
Ready to test? Send "hi" to your business number!
""")

print("=" * 70)
