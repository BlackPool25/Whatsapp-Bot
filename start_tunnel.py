#!/usr/bin/env python3
"""
Start ngrok tunnel for WhatsApp bot
You still need to sign up at https://dashboard.ngrok.com/signup and get your authtoken
Then run: ngrok config add-authtoken YOUR_TOKEN
"""
from pyngrok import ngrok
import time

print("🚀 Starting ngrok tunnel...")
print("⚠️  Make sure you have configured your ngrok authtoken first!")
print("   Sign up: https://dashboard.ngrok.com/signup")
print("   Configure: ngrok config add-authtoken YOUR_TOKEN")
print()

try:
    # Start ngrok tunnel on port 5000
    public_url = ngrok.connect(5000)
    print(f"✅ Ngrok tunnel started successfully!")
    print(f"🌐 Public URL: {public_url}")
    print()
    print("📋 Next steps:")
    print(f"   1. Copy this URL: {public_url}")
    print(f"   2. Go to Meta Developer Console → WhatsApp → Configuration")
    print(f"   3. Set Webhook URL: {public_url}/webhook")
    print(f"   4. Set Verify Token: abc123")
    print(f"   5. Subscribe to 'messages' field")
    print()
    print("Press Ctrl+C to stop the tunnel...")
    
    # Keep the tunnel alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping ngrok tunnel...")
        ngrok.disconnect(public_url)
        print("✅ Tunnel stopped")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("💡 Solution:")
    print("   1. Sign up for ngrok: https://dashboard.ngrok.com/signup")
    print("   2. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("   3. Run: ngrok config add-authtoken YOUR_TOKEN")
    print("   4. Then run this script again")
