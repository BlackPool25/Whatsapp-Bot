from flask import Flask, request
import requests

app = Flask(__name__)

# ----- CONFIG -----
VERIFY_TOKEN = "abc123"  # Must match Meta dashboard
ACCESS_TOKEN = "EAAQHS1vY2GQBPvjzSbtZAaNJPxZCV7k1tZBb5vKZAhcxgXaczuqmWs0IlapJvxlomVuo1dDZCJAfHh7Vfbf2mO9A5PZATZBrhKInCzRjGUubYQQ8vZC9V1OvWicjWfUQVD6J9XXIGbY8pZBZCsKlJMiSy4QVZALyZAyfqECjYwCfYo1U6al5SNuazVlbtvPw04vaWCQTkgQe2kcRuZCgVK3ZBZAywtMrotvymvkoFMoZCAcZBjPKY"
PHONE_NUMBER_ID = "883706248149866"

# Keep track of greeted users
user_greeted = {}

# ----- HELPER FUNCTION TO SEND WHATSAPP MESSAGE -----
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Sent message response:", response.json())

# ----- FLASK WEBHOOK -----
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification challenge from Meta
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("Received:", data)

        try:
            # Check for messages
            changes = data.get("entry", [])[0].get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    from_number = message["from"]
                    msg_type = message.get("type")

                    # ----- Handle text messages -----
                    if msg_type == "text":
                        user_text = message["text"]["body"].strip().lower()

                        if user_text in ["hi", "hello"] and not user_greeted.get(from_number):
                            reply = ("👋 Hey there! Welcome!\n"
                                     "Please send me a text, photo, or video and I will respond accordingly.")
                            user_greeted[from_number] = True
                        else:
                            reply = f"✅ Text received: {message['text']['body']}"

                    # ----- Handle image messages -----
                    elif msg_type == "image":
                        reply = "🖼 Photo uploaded successfully!"

                    # ----- Handle video messages -----
                    elif msg_type == "video":
                        reply = "🎥 Video uploaded successfully!"

                    else:
                        reply = "⚠ Unsupported message type."

                    # Send reply
                    send_whatsapp_message(from_number, reply)

        except Exception as e:
            print("Error processing message:", e)

        return "ok", 200

# ----- RUN FLASK SERVER -----
if __name__ == "__main__":
    app.run(port=5000)
