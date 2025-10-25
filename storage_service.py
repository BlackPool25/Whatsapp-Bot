"""
Storage Service - Handles all Supabase storage and database operations
"""
import uuid
import time
import mimetypes
from datetime import datetime
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, FILE_TYPE_MAPPINGS

# Supabase client (lazy initialization)
supabase: Client = None


def get_supabase_client():
    """Get or create Supabase client instance"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


def get_file_extension(filename, mime_type=None):
    """Extract file extension from filename or mime type"""
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    elif mime_type:
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


def upload_to_supabase(file_content, bucket_name, filename):
    """
    Upload file to Supabase storage bucket
    
    Args:
        file_content (bytes): File content to upload
        bucket_name (str): Supabase storage bucket name
        filename (str): Unique filename
    
    Returns:
        str: Public URL of uploaded file or None on error
    """
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


def store_detection_history(user_id, session_id, file_url, filename, file_type, 
                           file_size, file_extension, detection_result=None, 
                           confidence_score=None):
    """
    Store file metadata in detection_history table
    
    Args:
        user_id (str): User ID (can be None for anonymous users)
        session_id (str): Session ID (phone number or temp session)
        file_url (str): Public URL of uploaded file
        filename (str): Filename
        file_type (str): File type category (image, video, document)
        file_size (int): File size in bytes
        file_extension (str): File extension
        detection_result (str, optional): Detection result
        confidence_score (float, optional): Confidence score
    
    Returns:
        dict: Detection record or None on error
    """
    try:
        client = get_supabase_client()
        data = {
            "user_id": user_id,
            "session_id": session_id,
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


def get_user_from_token(token):
    """
    Extract user_id from Bearer token (JWT)
    
    Args:
        token (str): JWT token
    
    Returns:
        str: User ID or None
    """
    try:
        client = get_supabase_client()
        user = client.auth.get_user(token)
        return user.user.id if user and user.user else None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None
