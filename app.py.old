from flask import Flask, request, jsonify
import requests
import os
import uuid
import time
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import mimetypes
from functools import wraps
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# ----- CONFIG -----
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "abc123")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client (lazy initialization)
supabase: Client = None

def get_supabase_client():
    """Get or create Supabase client instance"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

# Keep track of greeted users
user_greeted = {}

# File type mappings
FILE_TYPE_MAPPINGS = {
    'image': {
        'extensions': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'],
        'bucket': 'image-uploads',
        'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic']
    },
    'video': {
        'extensions': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        'bucket': 'video-uploads',
        'mime_types': ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
    },
    'document': {
        'extensions': ['pdf', 'doc', 'docx', 'txt', 'csv'],
        'bucket': 'text-uploads',
        'mime_types': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/csv']
    }
}

# ----- HELPER FUNCTIONS -----

def get_file_extension(filename, mime_type=None):
    """Extract file extension from filename or mime type"""
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    elif mime_type:
        # Try to guess extension from MIME type
        ext = mimetypes.guess_extension(mime_type)
        return ext.lstrip('.') if ext else None
    return None


def determine_file_type_and_bucket(extension, mime_type=None):
    """Determine file type category and appropriate bucket based on extension or MIME type"""
    if extension:
        for file_type, config in FILE_TYPE_MAPPINGS.items():
            if extension in config['extensions']:
                return file_type, config['bucket']
    
    if mime_type:
        for file_type, config in FILE_TYPE_MAPPINGS.items():
            if mime_type in config['mime_types']:
                return file_type, config['bucket']
    
    # Default to text-uploads for unknown types
    return 'document', 'text-uploads'


def generate_unique_filename(user_id, original_filename, session_id=None):
    """Generate unique filename to prevent collisions"""
    timestamp = int(time.time())
    random_id = str(uuid.uuid4())[:8]
    extension = get_file_extension(original_filename) if original_filename else 'bin'
    
    # Sanitize original filename (remove extension and special chars)
    if original_filename:
        base_name = original_filename.rsplit('.', 1)[0]
        base_name = ''.join(c for c in base_name if c.isalnum() or c in ['-', '_'])[:50]
    else:
        base_name = 'file'
    
    # Use user_id if available, otherwise use session_id
    identifier = user_id or session_id or 'unknown'
    
    return f"{identifier}_{timestamp}_{random_id}_{base_name}.{extension}"


def generate_temp_session_id():
    """Generate a temporary session ID for anonymous users"""
    return f"temp_{str(uuid.uuid4())[:16]}"


def get_or_create_anonymous_session(phone_number):
    """Create or retrieve anonymous session ID for non-logged-in users"""
    # Use phone number hash as a consistent anonymous identifier
    anonymous_id = f"anon_{str(uuid.uuid5(uuid.NAMESPACE_DNS, phone_number))[:16]}"
    return anonymous_id


def download_whatsapp_media(media_id):
    """Download media file from WhatsApp"""
    try:
        # Step 1: Get media URL
        url = f"https://graph.facebook.com/v17.0/{media_id}"
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error getting media URL: {response.text}")
            return None, None, None
        
        media_data = response.json()
        media_url = media_data.get('url')
        mime_type = media_data.get('mime_type')
        
        if not media_url:
            print("No media URL found")
            return None, None, None
        
        # Step 2: Download the actual file
        download_response = requests.get(media_url, headers=headers)
        
        if download_response.status_code != 200:
            print(f"Error downloading media: {download_response.text}")
            return None, None, None
        
        return download_response.content, mime_type, media_data
    
    except Exception as e:
        print(f"Error in download_whatsapp_media: {e}")
        return None, None, None


def upload_to_supabase(file_content, bucket_name, filename):
    """Upload file to Supabase storage bucket"""
    try:
        client = get_supabase_client()
        response = client.storage.from_(bucket_name).upload(
            path=filename,
            file=file_content,
            file_options={"content-type": "application/octet-stream"}
        )
        
        # Get public URL
        public_url = client.storage.from_(bucket_name).get_public_url(filename)
        
        return public_url
    
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None


def store_detection_history(user_id, session_id, file_url, filename, file_type, file_size, file_extension, detection_result=None, confidence_score=None):
    """Store file metadata in detection_history table"""
    try:
        client = get_supabase_client()
        data = {
            "user_id": user_id,  # Can be None for anonymous users
            "session_id": session_id,  # Phone number or temp session ID
            "file_url": file_url,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "file_extension": file_extension,
            "detection_result": detection_result,
            "confidence_score": confidence_score,
            "is_file_available": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = client.table("detection_history").insert(data).execute()
        return response.data[0] if response.data else None
    
    except Exception as e:
        print(f"Error storing detection history: {e}")
        return None


def handle_file_upload(message, from_number, user_id=None):
    """Handle file upload from WhatsApp bot"""
    try:
        # Determine message type
        msg_type = message.get("type")
        
        # Extract media information based on type
        media_id = None
        original_filename = None
        mime_type = None
        
        if msg_type == "image":
            media_id = message.get("image", {}).get("id")
            mime_type = message.get("image", {}).get("mime_type")
            original_filename = message.get("image", {}).get("filename", f"image_{int(time.time())}")
        elif msg_type == "video":
            media_id = message.get("video", {}).get("id")
            mime_type = message.get("video", {}).get("mime_type")
            original_filename = message.get("video", {}).get("filename", f"video_{int(time.time())}")
        elif msg_type == "document":
            media_id = message.get("document", {}).get("id")
            mime_type = message.get("document", {}).get("mime_type")
            original_filename = message.get("document", {}).get("filename", f"document_{int(time.time())}")
        else:
            return False, "Unsupported file type"
        
        if not media_id:
            return False, "No media ID found"
        
        # For WhatsApp users, session_id is the phone number
        session_id = from_number
        
        # Download media from WhatsApp
        file_content, detected_mime_type, media_data = download_whatsapp_media(media_id)
        
        if not file_content:
            return False, "Failed to download file from WhatsApp"
        
        # Use detected MIME type if available
        mime_type = detected_mime_type or mime_type
        
        # Determine file type and bucket
        extension = get_file_extension(original_filename, mime_type)
        file_type, bucket_name = determine_file_type_and_bucket(extension, mime_type)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(user_id, original_filename, session_id)
        
        # Upload to Supabase
        file_url = upload_to_supabase(file_content, bucket_name, unique_filename)
        
        if not file_url:
            return False, "Failed to upload file to storage"
        
        # Store metadata in database
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
            return False, "Failed to store file metadata"
        
        return True, {
            "file_url": file_url,
            "filename": unique_filename,
            "file_type": file_type,
            "bucket": bucket_name,
            "size": file_size,
            "record_id": detection_record.get("id")
        }
    
    except Exception as e:
        print(f"Error in handle_file_upload: {e}")
        return False, str(e)


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
                            reply = ("👋 Hey there! Welcome to Deepfake Detector!\n"
                                     "Please send me a photo, video, or document and I will analyze it for deepfake detection.")
                            user_greeted[from_number] = True
                        else:
                            reply = f"✅ Text received: {message['text']['body']}\n\n"
                            reply += "💡 To detect deepfakes, please send an image, video, or document file."

                    # ----- Handle image messages -----
                    elif msg_type == "image":
                        success, result = handle_file_upload(message, from_number)
                        if success:
                            reply = f"🖼 Image uploaded successfully!\n\n"
                            reply += f"📁 File: {result['filename']}\n"
                            reply += f"📊 Type: {result['file_type']}\n"
                            reply += f"💾 Size: {result['size']} bytes\n"
                            reply += f"🔗 Bucket: {result['bucket']}\n\n"
                            reply += "🔍 Analyzing for deepfakes..."
                        else:
                            reply = f"❌ Error uploading image: {result}"

                    # ----- Handle video messages -----
                    elif msg_type == "video":
                        success, result = handle_file_upload(message, from_number)
                        if success:
                            reply = f"🎥 Video uploaded successfully!\n\n"
                            reply += f"📁 File: {result['filename']}\n"
                            reply += f"📊 Type: {result['file_type']}\n"
                            reply += f"💾 Size: {result['size']} bytes\n"
                            reply += f"🔗 Bucket: {result['bucket']}\n\n"
                            reply += "🔍 Analyzing for deepfakes..."
                        else:
                            reply = f"❌ Error uploading video: {result}"
                    
                    # ----- Handle document messages -----
                    elif msg_type == "document":
                        success, result = handle_file_upload(message, from_number)
                        if success:
                            reply = f"📄 Document uploaded successfully!\n\n"
                            reply += f"📁 File: {result['filename']}\n"
                            reply += f"📊 Type: {result['file_type']}\n"
                            reply += f"💾 Size: {result['size']} bytes\n"
                            reply += f"🔗 Bucket: {result['bucket']}\n\n"
                            reply += "🔍 Analyzing for deepfakes..."
                        else:
                            reply = f"❌ Error uploading document: {result}"

                    else:
                        reply = "⚠ Unsupported message type. Please send an image, video, or document."

                    # Send reply
                    send_whatsapp_message(from_number, reply)

        except Exception as e:
            print("Error processing message:", e)

        return "ok", 200


# ----- WEB API ENDPOINTS -----

def get_user_from_token():
    """Extract user_id from Bearer token (JWT)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        # Verify JWT token with Supabase
        client = get_supabase_client()
        user = client.auth.get_user(token)
        return user.user.id if user and user.user else None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Handle file uploads from web application
    Supports both authenticated and anonymous users
    
    Form data:
    - file: The file to upload (required)
    - session_id: Session ID for anonymous users (optional, will be generated if not provided)
    - user_id: User ID for authenticated users (optional, can be extracted from Bearer token)
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get user_id from Bearer token or form data
        user_id = get_user_from_token()
        if not user_id:
            user_id = request.form.get('user_id')
        
        # Get or generate session_id
        session_id = request.form.get('session_id')
        if not session_id and not user_id:
            # Generate temporary session ID for anonymous users
            session_id = generate_temp_session_id()
        
        # Read file content
        file_content = file.read()
        original_filename = file.filename
        
        # Determine file type and bucket
        extension = get_file_extension(original_filename)
        file_type, bucket_name = determine_file_type_and_bucket(extension)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(user_id, original_filename, session_id)
        
        # Upload to Supabase
        file_url = upload_to_supabase(file_content, bucket_name, unique_filename)
        
        if not file_url:
            return jsonify({"error": "Failed to upload file to storage"}), 500
        
        # Store metadata in database
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
    """
    Fetch detection history with conditional logic:
    1. If user_id is NOT NULL (logged-in user): Return ALL their records regardless of session_id
    2. If user_id IS NULL AND session_id exists: Return only records matching that session_id
    3. If user_id IS NULL AND session_id doesn't exist: Return error "Session not found"
    
    Query parameters:
    - session_id: Session ID for anonymous users (optional)
    
    Headers:
    - Authorization: Bearer token for authenticated users (optional)
    """
    try:
        client = get_supabase_client()
        
        # Get user_id from Bearer token
        user_id = get_user_from_token()
        
        # Get session_id from query params
        session_id = request.args.get('session_id')
        
        # Query logic
        if user_id:
            # Logged-in user: Return ALL their records regardless of session_id
            response = client.table("detection_history").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        elif session_id:
            # Anonymous user with session_id: Return only records matching that session_id
            response = client.table("detection_history").select("*").is_("user_id", "null").eq("session_id", session_id).order("created_at", desc=True).execute()
        else:
            # No user_id and no session_id: Error
            return jsonify({"error": "Session not found. Please provide a valid session_id or authentication token."}), 400
        
        return jsonify({
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }), 200
    
    except Exception as e:
        print(f"Error in api_history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<record_id>", methods=["GET"])
def api_history_detail(record_id):
    """
    Fetch a specific detection record by ID
    
    Path parameters:
    - record_id: The UUID of the detection record
    
    Headers:
    - Authorization: Bearer token for authenticated users (optional)
    
    Query parameters:
    - session_id: Session ID for anonymous users (optional)
    """
    try:
        client = get_supabase_client()
        
        # Get user_id from Bearer token
        user_id = get_user_from_token()
        
        # Get session_id from query params
        session_id = request.args.get('session_id')
        
        # Fetch the record
        response = client.table("detection_history").select("*").eq("id", record_id).execute()
        
        if not response.data:
            return jsonify({"error": "Record not found"}), 404
        
        record = response.data[0]
        
        # Check access permissions
        if record.get("user_id"):
            # Record belongs to a logged-in user
            if user_id != record.get("user_id"):
                return jsonify({"error": "Unauthorized access"}), 403
        else:
            # Record belongs to anonymous user, check session_id
            if not session_id or session_id != record.get("session_id"):
                return jsonify({"error": "Unauthorized access"}), 403
        
        return jsonify({
            "success": True,
            "data": record
        }), 200
    
    except Exception as e:
        print(f"Error in api_history_detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/session", methods=["POST"])
def api_create_session():
    """
    Generate a new temporary session ID for anonymous users
    """
    try:
        session_id = generate_temp_session_id()
        
        return jsonify({
            "success": True,
            "session_id": session_id
        }), 201
    
    except Exception as e:
        print(f"Error in api_create_session: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "whatsapp-bot-deepfake-detector"}), 200


# ----- RUN FLASK SERVER -----
if __name__ == "__main__":
    app.run(port=5000)
