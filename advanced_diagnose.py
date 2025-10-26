#!/usr/bin/env python3
"""
Advanced Webhook Troubleshooting - Check ALL possible issues
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🔍 ADVANCED WHATSAPP WEBHOOK TROUBLESHOOTING")
print("=" * 80)

ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

issues = []
fixes = []

print("\n📋 CRITICAL CHECKS (Top reasons webhooks don't work):")
print("-" * 80)

# Check 1: App Mode
print("\n1. ⚠️  APP MODE (MOST COMMON ISSUE)")
print("   Meta apps in 'Development Mode' often don't receive webhooks!")
print()
print("   ✅ HOW TO FIX:")
print("   → Go to: https://developers.facebook.com/apps/")
print("   → Select your app")
print("   → Top right corner: Look for 'Development' or 'Live' mode toggle")
print("   → If it says 'Development': Switch to 'Live' mode")
print("   → Note: You may need Business Verification for some apps")
issues.append("Check if app is in Live mode (not Development mode)")

# Check 2: Access Token
print("\n2. 🔑 ACCESS TOKEN STATUS")
if ACCESS_TOKEN:
    if len(ACCESS_TOKEN) < 50:
        print("   ❌ Token looks too short - might be invalid")
        issues.append("Access token appears invalid")
        fixes.append("Get new token from Meta Console → WhatsApp → API Setup")
    else:
        # Test the token
        try:
            url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}"
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ Access token is valid")
                data = response.json()
                print(f"   Business Number: {data.get('display_phone_number', 'N/A')}")
            elif response.status_code == 190 or response.status_code == 401:
                print("   ❌ Access token is EXPIRED or INVALID")
                issues.append("Access token expired/invalid")
                fixes.append("Generate new token: Meta Console → WhatsApp → API Setup → Copy new temporary token")
            elif response.status_code == 400:
                print("   ❌ API Access Blocked - Token may be expired or lacks permissions")
                issues.append("API access blocked")
                fixes.append("Generate new access token with proper permissions")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error checking token: {e}")
            issues.append("Cannot verify access token")
else:
    print("   ❌ No access token found")
    issues.append("Missing access token")

# Check 3: Webhook URL accessibility
print("\n3. 🌐 WEBHOOK URL ACCESSIBILITY")
try:
    ngrok_response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
    tunnels = ngrok_response.json()
    
    if tunnels.get("tunnels"):
        https_url = None
        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                https_url = tunnel["public_url"]
                break
        
        if https_url:
            print(f"   ✅ Ngrok URL: {https_url}")
            print(f"   ⚠️  IMPORTANT: This URL must be configured in Meta Console!")
            print(f"   → Webhook URL: {https_url}/webhook")
            
            # Test if webhook is accessible from outside
            try:
                test_response = requests.get(
                    f"{https_url}/webhook",
                    params={
                        "hub.verify_token": "abc123",
                        "hub.challenge": "test123",
                        "hub.mode": "subscribe"
                    },
                    timeout=10
                )
                if test_response.text == "test123":
                    print("   ✅ Webhook is publicly accessible")
                else:
                    print("   ⚠️  Webhook verification issue")
                    issues.append("Webhook verification not working correctly")
            except:
                print("   ⚠️  Could not test webhook from outside")
        else:
            print("   ❌ No HTTPS ngrok tunnel found")
            issues.append("No HTTPS ngrok tunnel")
            fixes.append("Make sure ngrok is running: ngrok http 5000")
    else:
        print("   ❌ Ngrok is not running")
        issues.append("Ngrok not running")
        fixes.append("Start ngrok: ngrok http 5000")
except:
    print("   ❌ Cannot connect to ngrok")
    issues.append("Ngrok not accessible")
    fixes.append("Start ngrok: ngrok http 5000")

# Check 4: Local server
print("\n4. 🖥️  LOCAL FLASK SERVER")
try:
    health = requests.get("http://localhost:5000/health", timeout=5)
    if health.status_code == 200:
        print("   ✅ Flask server is running")
    else:
        print(f"   ⚠️  Server responded with {health.status_code}")
except:
    print("   ❌ Flask server is NOT running")
    issues.append("Flask server not running")
    fixes.append("Start server: /home/lightdesk/Projects/whatsapp/venv/bin/python app.py")

print("\n" + "=" * 80)
print("🎯 MOST LIKELY ISSUES (based on checks above):")
print("=" * 80)

if issues:
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
else:
    print("✅ All automatic checks passed!")

if fixes:
    print("\n" + "=" * 80)
    print("🔧 FIXES TO APPLY:")
    print("=" * 80)
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix}")

print("\n" + "=" * 80)
print("📝 MANUAL VERIFICATION CHECKLIST:")
print("=" * 80)
print("""
Go to Meta Developer Console and verify each item:

□ 1. APP MODE
   → https://developers.facebook.com/apps/ → Your App
   → Top right: Should say "Live" not "Development"
   → If Development: Switch to Live mode

□ 2. WEBHOOK CONFIGURATION  
   → WhatsApp → Configuration → Webhook section
   → Callback URL is set to your ngrok URL + /webhook
   → Verify token is "abc123"
   → Green checkmark ✓ appears (webhook verified)

□ 3. WEBHOOK SUBSCRIPTION
   → Same Configuration page
   → Scroll to "Webhook fields"
   → "messages" field is SUBSCRIBED (checked)

□ 4. TEST PHONE NUMBER ADDED
   → WhatsApp → API Setup
   → "To" field → "Manage phone number list"
   → Your phone number is in the list
   → Status shows "Verified"

□ 5. BUSINESS PHONE NUMBER
   → WhatsApp → API Setup
   → "From" field shows your business number
   → You're sending messages TO this number (not from it!)

□ 6. ACCESS TOKEN FRESH
   → WhatsApp → API Setup
   → Copy the Temporary access token
   → Update your .env file if it's different
   → Tokens expire after 24 hours!

□ 7. PERMISSIONS
   → App Dashboard → Permissions
   → "whatsapp_business_messaging" is approved/active
   → "whatsapp_business_management" is approved/active
""")

print("=" * 80)
print("🧪 TEST YOUR WEBHOOK MANUALLY:")
print("=" * 80)
print("""
In Meta Developer Console:
1. Go to WhatsApp → Configuration
2. Find "Test" button near webhook settings
3. Click "Test" → "Send test request"
4. Check your Flask terminal - you should see the test payload

If test works but real messages don't:
→ 99% chance your app is in Development mode instead of Live mode!
""")

print("=" * 80)
print("📞 WHAT NUMBER ARE YOU MESSAGING?")
print("=" * 80)
print("""
CRITICAL: You need to message YOUR BUSINESS NUMBER, not someone else's!

To find your business number:
1. Meta Console → WhatsApp → API Setup
2. Look at "From" field
3. That's the number to message from WhatsApp!

Example: If your business number is +1 555 123 4567
→ Open WhatsApp app
→ Start chat with +15551234567
→ Send "hi"
→ Bot should reply!
""")

print("=" * 80)
