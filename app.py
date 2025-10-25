"""
WhatsApp Deepfake Detector Bot - Main Application
"""
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from config import VERIFY_TOKEN, MAX_CONTENT_LENGTH
from whatsapp_service import send_whatsapp_message, mark_message_as_read
from storage_service import (
    get_supabase_client,
    get_file_extension,
    determine_file_type_and_bucket,
    generate_unique_filename,
    generate_temp_session_id,
    upload_to_supabase,
    store_detection_history,
    get_user_from_token
)
from message_handler import process_whatsapp_message

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """WhatsApp webhook endpoint"""
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if token == VERIFY_TOKEN:
            print("Webhook verified successfully")
            return challenge
        else:
            print("Webhook verification failed")
            return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("Webhook received:", data)

        try:
            entry = data.get("entry", [])
            if not entry:
                return "ok", 200
            
            changes = entry[0].get("changes", [])
            
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    from_number = message.get("from")
                    message_id = message.get("id")
                    
                    if not from_number:
                        continue
                    
                    if message_id:
                        mark_message_as_read(message_id)
                    
                    reply = process_whatsapp_message(message, from_number)
                    
                    if reply:
                        send_whatsapp_message(from_number, reply)

        except Exception as e:
            print(f"Error processing webhook: {e}")
            import traceback
            traceback.print_exc()

        return "ok", 200


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Handle file uploads from web application"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        user_id = get_user_from_token_header()
        if not user_id:
            user_id = request.form.get('user_id')
        
        session_id = request.form.get('session_id')
        if not session_id and not user_id:
            session_id = generate_temp_session_id()
        
        file_content = file.read()
        original_filename = secure_filename(file.filename)
        
        extension = get_file_extension(original_filename)
        file_type, bucket_name = determine_file_type_and_bucket(extension)
        
        unique_filename = generate_unique_filename(user_id, original_filename, session_id)
        
        file_url = upload_to_supabase(file_content, bucket_name, unique_filename)
        
        if not file_url:
            return jsonify({"error": "Failed to upload file to storage"}), 500
        
        file_size = len(file_content)
        detection_record = store_detection_history(
            user_id=user_id,
            session_id=session_id,
            file_url=file_url,
            filename=unique_filename,
            file_type=file_type,
            file_size=file_size,
            file_extension=extension or 'unknown'
        )
        
        if not detection_record:
            return jsonify({"error": "Failed to store file metadata"}), 500
        
        return jsonify({
            "success": True,
            "data": {
                "id": detection_record.get("id"),
                "file_url": file_url,
                "filename": unique_filename,
                "file_type": file_type,
                "bucket": bucket_name,
                "size": file_size,
                "user_id": user_id,
                "session_id": session_id,
                "created_at": detection_record.get("created_at")
            }
        }), 201
    
    except Exception as e:
        print(f"Error in api_upload: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def api_history():
    """Fetch detection history"""
    try:
        client = get_supabase_client()
        user_id = get_user_from_token_header()
        session_id = request.args.get('session_id')
        
        if user_id:
            response = client.table("detection_history").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        elif session_id:
            response = client.table("detection_history").select("*").is_("user_id", "null").eq("session_id", session_id).order("created_at", desc=True).execute()
        else:
            return jsonify({"error": "Session not found. Please provide session_id or authentication token."}), 400
        
        return jsonify({"success": True, "data": response.data, "count": len(response.data)}), 200
    
    except Exception as e:
        print(f"Error in api_history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<record_id>", methods=["GET"])
def api_history_detail(record_id):
    """Fetch a specific detection record by ID"""
    try:
        client = get_supabase_client()
        user_id = get_user_from_token_header()
        session_id = request.args.get('session_id')
        
        response = client.table("detection_history").select("*").eq("id", record_id).execute()
        
        if not response.data:
            return jsonify({"error": "Record not found"}), 404
        
        record = response.data[0]
        
        if record.get("user_id"):
            if user_id != record.get("user_id"):
                return jsonify({"error": "Unauthorized access"}), 403
        else:
            if not session_id or session_id != record.get("session_id"):
                return jsonify({"error": "Unauthorized access"}), 403
        
        return jsonify({"success": True, "data": record}), 200
    
    except Exception as e:
        print(f"Error in api_history_detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/session", methods=["POST"])
def api_create_session():
    """Generate a new temporary session ID for anonymous users"""
    try:
        session_id = generate_temp_session_id()
        return jsonify({"success": True, "session_id": session_id}), 201
    except Exception as e:
        print(f"Error in api_create_session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "whatsapp-bot-deepfake-detector"}), 200


def get_user_from_token_header():
    """Extract user_id from Authorization Bearer token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return get_user_from_token(token)


if __name__ == "__main__":
    print("🚀 Starting WhatsApp Deepfake Detector Bot...")
    print("📱 Webhook endpoint: /webhook")
    print("🌐 API endpoints: /api/*")
    print("💚 Health check: /health")
    app.run(host='0.0.0.0', port=5000, debug=True)
