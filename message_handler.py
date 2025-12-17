"""
Message Handler - Processes different types of WhatsApp messages
"""
import time
import os
from whatsapp_service import send_whatsapp_message, download_whatsapp_media
from storage_service import (
    get_file_extension, 
    determine_file_type_and_bucket,
    generate_unique_filename,
    upload_to_supabase,
    store_detection_history,
    get_supabase_client
)
from modal_service import detect_video_multimodal, detect_image_ai, detect_text_ai, ModalDetectionError
from config import WELCOME_MESSAGE, HELP_MESSAGE


# Track user greetings (in-memory store)
user_greeted = {}

# Track user state - what type of content they're expecting to send
user_state = {}
# States: None (no choice made), 'image', 'video', 'text'


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
        user_state[from_number] = None  # Reset state
        return WELCOME_MESSAGE
    
    # Handle specific commands
    if user_text in ["hi", "hello", "hey", "start"]:
        user_state[from_number] = None  # Reset state
        return WELCOME_MESSAGE
    elif user_text in ["help", "info", "?", "support"]:
        return HELP_MESSAGE
    elif user_text in ["1", "image", "photo", "picture"]:
        user_state[from_number] = 'image'
        return "🖼 Great! Please send me an *image* that you want to analyze for deepfakes.\n\nI'm ready to receive your image."
    elif user_text in ["2", "video", "vid"]:
        user_state[from_number] = 'video'
        return "🎥 Great! Please send me a *video* that you want to analyze for deepfakes.\n\nI'm ready to receive your video."
    elif user_text in ["3", "text", "txt"]:
        user_state[from_number] = 'text'
        return "📝 Great! Please send me the *text* that you want to analyze.\n\nType your message below."
    elif user_state.get(from_number) == 'text':
        # User has chosen text option and is now sending text to analyze
        user_state[from_number] = None  # Reset state after processing
        return f"✅ Text received for analysis:\n\n\"{text_body}\"\n\n🔍 Analyzing for AI-generated content...\n⏳ This may take a moment...\n\n{HELP_MESSAGE}"
    else:
        # User sent text but hasn't chosen an option
        return f"❓ I'm not sure what you'd like to do.\n\n{WELCOME_MESSAGE}"


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
            user_state[from_number] = None
            return False, "Please choose an option first (1 for Image, 2 for Video, 3 for Text)"
        
        # Determine message type
        msg_type = message.get("type")
        
        # Check if user has selected the correct option
        expected_state = user_state.get(from_number)
        
        if expected_state is None:
            return False, "Please choose an option first:\n\n1️⃣ Send *1* for Image Analysis\n2️⃣ Send *2* for Video Analysis\n3️⃣ Send *3* for Text Analysis"
        
        # Validate that the media type matches the user's choice
        if msg_type == "image" and expected_state != 'image':
            return False, f"⚠️ You selected option '{expected_state}' but sent an image.\n\nPlease send the correct type of content, or type 'start' to choose again."
        elif msg_type == "video" and expected_state != 'video':
            return False, f"⚠️ You selected option '{expected_state}' but sent a video.\n\nPlease send the correct type of content, or type 'start' to choose again."
        elif msg_type == "document":
            # For documents, we need to check the mime type
            mime_type = message.get("document", {}).get("mime_type", "")
            if expected_state == 'image' and not mime_type.startswith('image/'):
                return False, f"⚠️ You selected 'image' but sent a document.\n\nPlease send an image file, or type 'start' to choose again."
            elif expected_state == 'video' and not mime_type.startswith('video/'):
                return False, f"⚠️ You selected 'video' but sent a document.\n\nPlease send a video file, or type 'start' to choose again."
        
        # Extract media information based on type
        media_id = None
        original_filename = None
        mime_type = None
        
        if msg_type == "image":
            media_id = message.get("image", {}).get("id")
            mime_type = message.get("image", {}).get("mime_type", "image/jpeg")
            # WhatsApp doesn't provide filename for images, create one with extension
            original_filename = message.get("image", {}).get("filename")
            if not original_filename or '.' not in original_filename:
                # Determine extension from mime type
                ext = "jpg" if "jpeg" in mime_type else mime_type.split('/')[-1] if '/' in mime_type else "jpg"
                original_filename = f"image_{int(time.time())}.{ext}"
        elif msg_type == "video":
            media_id = message.get("video", {}).get("id")
            mime_type = message.get("video", {}).get("mime_type", "video/mp4")
            original_filename = message.get("video", {}).get("filename")
            if not original_filename or '.' not in original_filename:
                ext = mime_type.split('/')[-1] if '/' in mime_type else "mp4"
                original_filename = f"video_{int(time.time())}.{ext}"
        elif msg_type == "document":
            media_id = message.get("document", {}).get("id")
            mime_type = message.get("document", {}).get("mime_type", "application/octet-stream")
            original_filename = message.get("document", {}).get("filename")
            if not original_filename or '.' not in original_filename:
                ext = mime_type.split('/')[-1] if '/' in mime_type else "bin"
                original_filename = f"document_{int(time.time())}.{ext}"
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
        
        record_id = detection_record.get("id")
        
        # Trigger Modal video detection for videos
        if file_type == 'video':
            try:
                print(f"🎥 Triggering balanced 3-layer video detection for {unique_filename}...")
                
                # Call Modal API to detect (synchronous with balanced pipeline)
                modal_response = detect_video_multimodal(
                    video_url=file_url,
                    enable_fail_fast=False  # Get all 3 layers for comprehensive analysis
                )
                
                print(f"✅ Video detection complete: {modal_response.get('final_verdict')}")
                
                # Format detailed detection result
                is_fake = modal_response.get('final_verdict') == 'FAKE'
                confidence = modal_response.get('confidence', 0)
                
                # Update detection record with full results
                supabase = get_supabase_client()
                supabase.table("detection_history").update({
                    "detection_result": modal_response.get('final_verdict'),
                    "confidence_score": int(confidence * 100),  # Convert to percentage
                    "detector_scores": {
                        "layers": [
                            {
                                "name": lr.get('layer_name'),
                                "verdict": 'FAKE' if lr.get('is_fake') else 'REAL',
                                "confidence": int(lr.get('confidence', 0) * 100),
                                "time": lr.get('processing_time', 0)
                            }
                            for lr in modal_response.get('layer_results', [])
                        ],
                        "stopped_at": modal_response.get('stopped_at_layer'),
                        "total_time": modal_response.get('total_time', 0)
                    },
                    "model_metadata": {
                        "model": "Balanced-3Layer-Pipeline-v1",
                        "layers": 3,
                        "weights": [0.80, 0.15, 0.05]
                    }
                }).eq("id", record_id).execute()
                
                # Store result for response formatting
                result["detection"] = modal_response
                
            except Exception as e:
                print(f"⚠️ Failed to trigger video detection: {e}")
                import traceback
                traceback.print_exc()
                # Mark as error in database
                try:
                    supabase = get_supabase_client()
                    supabase.table("detection_history").update({
                        "detection_result": "error",
                        "model_metadata": {"error": str(e)}
                    }).eq("id", record_id).execute()
                except:
                    pass
        
        # Trigger Modal image detection for images
        elif file_type == 'image':
            try:
                print(f"🖼️ Triggering AI image detection for {unique_filename}...")
                
                # Call Modal API to detect
                modal_response = detect_image_ai(
                    file_content=file_content,
                    mime_type=mime_type
                )
                
                print(f"✅ Image detection complete: {modal_response.get('top_prediction')}")
                
                # Map response to our format
                top_pred = modal_response.get('top_prediction', '').upper()
                is_fake = 'AI' in top_pred or 'FAKE' in top_pred
                confidence = modal_response.get('confidence', 0.5)
                
                # Update detection record
                supabase = get_supabase_client()
                supabase.table("detection_history").update({
                    "detection_result": "FAKE" if is_fake else "REAL",
                    "confidence_score": int(confidence * 100),
                    "detector_scores": {
                        "predictions": modal_response.get('predictions', []),
                        "top_prediction": modal_response.get('top_prediction')
                    },
                    "model_metadata": {
                        "model": "EfficientFormer-S2V1-Image-Detector"
                    }
                }).eq("id", record_id).execute()
                
                # Store result for response formatting
                result["detection"] = {
                    "final_verdict": "FAKE" if is_fake else "REAL",
                    "confidence": confidence,
                    "top_prediction": modal_response.get('top_prediction')
                }
                
            except ModalDetectionError as e:
                print(f"⚠️ Failed to trigger image detection: {e}")
                # Mark as error
                try:
                    supabase = get_supabase_client()
                    supabase.table("detection_history").update({
                        "detection_result": "error",
                        "model_metadata": {"error": str(e)}
                    }).eq("id", record_id).execute()
                except:
                    pass
        
        # Reset user state after successful upload
        user_state[from_number] = None
        
        return True, {
            "file_url": file_url,
            "filename": unique_filename,
            "file_type": file_type,
            "bucket": bucket_name,
            "size": file_size,
            "record_id": record_id,
            "msg_type": msg_type
        }
    
    except Exception as e:
        print(f"Error in handle_media_message: {e}")
        return False, str(e)


def format_media_response(msg_type, result):
    """
    Format response message for media uploads with detection results
    
    Args:
        msg_type (str): Message type (image, video, document)
        result (dict): Upload result with optional detection data
    
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
    response += f"💾 Size: {result['size']:,} bytes\n\n"
    
    # Add detection results if available
    detection = result.get('detection')
    if detection and not detection.get('error'):
        # Handle video detection results (3-layer pipeline)
        if msg_type == "video":
            verdict = detection.get('final_verdict', 'UNKNOWN')
            confidence = detection.get('confidence', 0)
            
            # Verdict with emoji
            if verdict == 'FAKE':
                response += "🚨 *DEEPFAKE DETECTED*\n"
                response += f"⚠️ Confidence: {confidence:.1%}\n\n"
            else:
                response += "✅ *AUTHENTIC VIDEO*\n"
                response += f"✓ Confidence: {confidence:.1%}\n\n"
            
            # Layer breakdown
            response += "📊 *Analysis Breakdown:*\n"
            for lr in detection.get('layer_results', []):
                layer_name = lr.get('layer_name', 'Unknown')
                layer_verdict = 'FAKE' if lr.get('is_fake') else 'REAL'
                layer_conf = lr.get('confidence', 0)
                layer_time = lr.get('processing_time', 0)
                
                # Simple layer names
                if 'Visual' in layer_name:
                    icon = "👁️"
                    name = "Visual Check"
                elif 'Temporal' in layer_name:
                    icon = "⏱️"
                    name = "Temporal Check"
                elif 'Audio' in layer_name:
                    icon = "🔊"
                    name = "Audio Check"
                else:
                    icon = "🔍"
                    name = layer_name
                
                response += f"{icon} {name}: {layer_verdict} ({layer_conf:.0%}) [{layer_time:.1f}s]\n"
            
            total_time = detection.get('total_time', 0)
            response += f"\n⏱️ Total Analysis: {total_time:.2f}s\n"
            response += f"🤖 Model: Balanced-3Layer-Pipeline-v1"
        
        # Handle image detection results (EfficientFormer)
        elif msg_type == "image":
            top_pred = detection.get('top_prediction', 'UNKNOWN')
            confidence = detection.get('confidence', 0)
            is_ai = detection.get('is_ai_generated', False)
            
            # Verdict with emoji
            if is_ai:
                response += "🤖 *AI-GENERATED IMAGE*\n"
                response += f"⚠️ Confidence: {confidence:.1%}\n\n"
            else:
                response += "✅ *REAL PHOTOGRAPH*\n"
                response += f"✓ Confidence: {confidence:.1%}\n\n"
            
            response += f"📊 Classification: {top_pred}\n"
            response += f"🤖 Model: EfficientFormer-L1"
        
    elif msg_type == "video" and not detection:
        response += "🔍 Analyzing for deepfakes...\n"
        response += "⏳ This may take a moment..."
    elif msg_type == "image" and not detection:
        response += "🔍 Analyzing for AI generation...\n"
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
