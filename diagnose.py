#!/usr/bin/env python3
"""
Diagnostic tool for WhatsApp Bot
Checks common issues and provides troubleshooting steps
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 WhatsApp Bot Diagnostics")
print("=" * 60)

# Check 1: Environment Variables
print("\n1. Checking environment variables...")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

if VERIFY_TOKEN:
    print(f"   ✅ VERIFY_TOKEN: {VERIFY_TOKEN}")
else:
    print("   ❌ VERIFY_TOKEN: Not set")

if ACCESS_TOKEN:
    print(f"   ✅ WHATSAPP_ACCESS_TOKEN: {ACCESS_TOKEN[:20]}...")
else:
    print("   ❌ WHATSAPP_ACCESS_TOKEN: Not set")

if PHONE_NUMBER_ID:
    print(f"   ✅ PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")
else:
    print("   ❌ PHONE_NUMBER_ID: Not set")

# Check 2: Local server
print("\n2. Checking local server...")
try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Local server is running on port 5000")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ⚠️  Server responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Local server is NOT running on port 5000")
    print("   💡 Start it with: /home/lightdesk/Projects/whatsapp/venv/bin/python app.py")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 3: Test webhook endpoint
print("\n3. Testing webhook endpoint...")
try:
    # Test GET request (verification)
    test_token = VERIFY_TOKEN or "test"
    test_challenge = "test_challenge_123"
    response = requests.get(
        "http://localhost:5000/webhook",
        params={
            "hub.verify_token": test_token,
            "hub.challenge": test_challenge,
            "hub.mode": "subscribe"
        },
        timeout=5
    )
    if response.text == test_challenge:
        print("   ✅ Webhook verification works correctly")
    else:
        print(f"   ⚠️  Webhook verification issue. Expected: {test_challenge}, Got: {response.text}")
except Exception as e:
    print(f"   ❌ Error testing webhook: {e}")

# Check 4: WhatsApp API Access
print("\n4. Checking WhatsApp API access...")
if ACCESS_TOKEN and PHONE_NUMBER_ID:
    try:
        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ WhatsApp API access is working")
            print(f"   Phone Number: {data.get('display_phone_number', 'N/A')}")
            print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
        elif response.status_code == 401:
            print("   ❌ Invalid ACCESS_TOKEN")
            print("   💡 Check your token in Meta Developer Console")
        elif response.status_code == 404:
            print("   ❌ Invalid PHONE_NUMBER_ID")
            print("   💡 Check your phone number ID in Meta Developer Console")
        else:
            print(f"   ⚠️  API responded with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error accessing WhatsApp API: {e}")
else:
    print("   ⚠️  Cannot check - missing ACCESS_TOKEN or PHONE_NUMBER_ID")

# Check 5: Test message sending (optional)
print("\n5. Message sending capability...")
print("   ℹ️  Skipped (requires recipient phone number)")

print("\n" + "=" * 60)
print("📋 TROUBLESHOOTING CHECKLIST:")
print("=" * 60)

issues_found = []

if not VERIFY_TOKEN or not ACCESS_TOKEN or not PHONE_NUMBER_ID:
    issues_found.append("Missing environment variables")
    
print("\n✅ Steps to fix common issues:")
print("\n1. WEBHOOK NOT VERIFIED IN META:")
print("   - Go to Meta Developer Console → WhatsApp → Configuration")
print("   - Click 'Edit' on Callback URL")
print(f"   - Set URL to your ngrok URL + /webhook")
print(f"   - Set Verify Token to: {VERIFY_TOKEN or 'abc123'}")
print("   - Click 'Verify and Save'")

print("\n2. NOT SUBSCRIBED TO WEBHOOK FIELDS:")
print("   - In the same Configuration page")
print("   - Find 'Webhook fields' section")
print("   - Make sure 'messages' is CHECKED/SUBSCRIBED")

print("\n3. PHONE NUMBER NOT ADDED FOR TESTING:")
print("   - Go to Meta Developer Console → WhatsApp → API Setup")
print("   - Under 'To' field, click 'Manage phone number list'")
print("   - Add your phone number and verify with OTP")

print("\n4. SENDING TO WRONG NUMBER:")
print("   - You should send messages TO your WhatsApp Business number")
print("   - Not from it!")
print("   - Find your business number in Meta Console")

print("\n5. APP NOT IN LIVE MODE:")
print("   - Some webhooks don't work in Development mode")
print("   - Check if your app needs to be in Live mode")

print("\n6. NGROK TUNNEL ISSUES:")
print("   - Make sure ngrok is still running")
print("   - Ngrok URLs expire after 2 hours on free plan")
print("   - You may need to restart ngrok and update webhook URL")

print("\n7. CHECK WEBHOOK LOGS:")
print("   - Watch your Flask app terminal for incoming requests")
print("   - You should see 'Webhook received:' when messages arrive")

print("\n" + "=" * 60)
print("🔗 USEFUL LINKS:")
print("   Meta Developer Console: https://developers.facebook.com/apps/")
print("   WhatsApp Cloud API Docs: https://developers.facebook.com/docs/whatsapp/cloud-api")
print("=" * 60)
