"""
Message Handler - Processes different types of WhatsApp messages
"""
import time
from whatsapp_service import send_whatsapp_message, download_whatsapp_media
from storage_service import (
    get_file_extension, 
    determine_file_type_and_bucket,
    generate_unique_filename,
    upload_to_supabase,
    store_detection_history
)
from config import WELCOME_MESSAGE, HELP_MESSAGE


# Track user greetings (in-memory store)
user_greeted = {}


def handle_text_message(from_number, text_body):
    """
    Handle incoming text messages
    
    Args:
        from_number (str): Sender's phone number
        text_body (str): Message text
    
    Returns:
        str: Reply message
    """
    user_text = text_body.strip().lower()
    
    # Check if user needs greeting
    if from_number not in user_greeted:
        user_greeted[from_number] = True
        return WELCOME_MESSAGE
    
    # Handle specific commands
    if user_text in ["hi", "hello", "hey", "start"]:
        return WELCOME_MESSAGE
    elif user_text in ["help", "info", "?", "support"]:
        return HELP_MESSAGE
    else:
        # Default response for any other text
        return f"✅ Text received: {text_body}\n\n{HELP_MESSAGE}"


def handle_media_message(message, from_number, user_id=None):
    """
    Handle incoming media messages (image, video, document)
    
    Args:
        message (dict): WhatsApp message object
        from_number (str): Sender's phone number
        user_id (str, optional): User ID if authenticated
    
    Returns:
        tuple: (success: bool, result: str or dict)
    """
    try:
        # Send initial greeting if user hasn't been greeted
        if from_number not in user_greeted:
            send_whatsapp_message(from_number, WELCOME_MESSAGE)
            user_greeted[from_number] = True
        
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
            "record_id": detection_record.get("id"),
            "msg_type": msg_type
        }
    
    except Exception as e:
        print(f"Error in handle_media_message: {e}")
        return False, str(e)


def format_media_response(msg_type, result):
    """
    Format response message for media uploads
    
    Args:
        msg_type (str): Message type (image, video, document)
        result (dict): Upload result
    
    Returns:
        str: Formatted response message
    """
    emoji_map = {
        "image": "🖼",
        "video": "🎥",
        "document": "📄"
    }
    
    emoji = emoji_map.get(msg_type, "📁")
    type_name = msg_type.capitalize()
    
    response = f"{emoji} {type_name} uploaded successfully!\n\n"
    response += f"📁 File: {result['filename']}\n"
    response += f"📊 Type: {result['file_type']}\n"
    response += f"💾 Size: {result['size']:,} bytes\n"
    response += f"🔗 Bucket: {result['bucket']}\n\n"
    response += "🔍 Analyzing for deepfakes...\n"
    response += "⏳ This may take a moment..."
    
    return response


def process_whatsapp_message(message, from_number):
    """
    Main message processor - routes to appropriate handler
    
    Args:
        message (dict): WhatsApp message object
        from_number (str): Sender's phone number
    
    Returns:
        str: Response message to send back
    """
    msg_type = message.get("type")
    
    # Handle text messages
    if msg_type == "text":
        text_body = message.get("text", {}).get("body", "")
        return handle_text_message(from_number, text_body)
    
    # Handle media messages (image, video, document)
    elif msg_type in ["image", "video", "document"]:
        success, result = handle_media_message(message, from_number)
        
        if success:
            return format_media_response(msg_type, result)
        else:
            error_msg = f"❌ Error processing {msg_type}: {result}\n\n"
            error_msg += "Please try again or contact support if the issue persists."
            return error_msg
    
    # Handle unsupported message types
    else:
        # Still greet new users even if they send unsupported content
        if from_number not in user_greeted:
            user_greeted[from_number] = True
            return WELCOME_MESSAGE
        else:
            return f"⚠ Unsupported message type '{msg_type}'.\n\n{HELP_MESSAGE}"
