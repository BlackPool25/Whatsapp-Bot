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
        print(f"✅ Supabase client initialized successfully")
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
        
        print(f"📤 Uploading to bucket: {bucket_name}, filename: {filename}")
        print(f"   File size: {len(file_content)} bytes")
        
        # Upload file with upsert option to overwrite if exists
        response = client.storage.from_(bucket_name).upload(
            path=filename,
            file=file_content,
            file_options={
                "content-type": "application/octet-stream",
                "upsert": "true"  # Allow overwriting existing files
            }
        )
        
        print(f"✅ Upload response: {response}")
        
        # Get public URL
        public_url = client.storage.from_(bucket_name).get_public_url(filename)
        
        print(f"🔗 Public URL generated: {public_url}")
        
        return public_url
    
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error uploading to Supabase bucket '{bucket_name}': {e}")
        print(f"   Filename: {filename}")
        print(f"   File size: {len(file_content)} bytes")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Full error: {error_str}")
        
        # Check specific error types
        if "not found" in error_str.lower() or "404" in error_str:
            print(f"   💡 Bucket '{bucket_name}' may not exist!")
            print(f"   Create it at: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets")
        elif "row-level security" in error_str.lower() or "403" in error_str or "unauthorized" in error_str.lower():
            print(f"\n   🔐 ROW-LEVEL SECURITY (RLS) POLICY ERROR!")
            print(f"   Your Supabase bucket has RLS enabled which blocks uploads.")
            print(f"\n   📋 TO FIX THIS:")
            print(f"   1. Go to: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets/{bucket_name}")
            print(f"   2. Click on 'Policies' tab")
            print(f"   3. Either:")
            print(f"      a) Click 'New Policy' → 'Allow public access' → Save")
            print(f"      b) Or disable RLS entirely (Configuration → Make bucket public)")
            print(f"\n   💡 For a WhatsApp bot, you typically want public uploads enabled.\n")
        elif "already exists" in error_str.lower() or "duplicate" in error_str.lower():
            print(f"   💡 File already exists, trying to get URL anyway...")
            try:
                # If file already exists, just return the public URL
                public_url = client.storage.from_(bucket_name).get_public_url(filename)
                print(f"   ✅ Retrieved existing file URL: {public_url}")
                return public_url
            except:
                pass
        
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
        
        # Ensure required fields have values (database has NOT NULL constraints)
        data = {
            "session_id": session_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": int(file_size),  # Ensure it's an integer
            "file_extension": file_extension,
            "detection_result": detection_result if detection_result else "pending",
            "confidence_score": float(confidence_score) if confidence_score is not None else 0.0,
        }
        
        # Add optional fields only if they have values
        if user_id:
            data["user_id"] = user_id
        if file_url:
            data["file_url"] = file_url
        
        # is_file_available defaults to true in database, but we can override
        data["is_file_available"] = True
        
        print(f"💾 Storing metadata in detection_history table...")
        print(f"   File: {filename}")
        print(f"   Type: {file_type}")
        print(f"   Extension: {file_extension}")
        print(f"   Detection result: {data['detection_result']}")
        print(f"   Confidence: {data['confidence_score']}")
        
        print(f"   Data to insert: {data}")
        
        response = client.table("detection_history").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ Metadata stored successfully! Record ID: {response.data[0].get('id')}")
            return response.data[0]
        else:
            print(f"⚠️ No data returned from insert operation")
            print(f"   Response: {response}")
            return None
    
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error storing detection history: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Data attempted: {data if 'data' in locals() else 'N/A'}")
        
        # Check for NOT NULL constraint violations
        if "not-null constraint" in error_str.lower() or "23502" in error_str:
            print(f"\n   ⚠️ NOT NULL CONSTRAINT VIOLATION!")
            print(f"   Some required fields in detection_history table are missing.")
            print(f"   The database schema requires certain fields to have values.")
            
            # Extract which column from error message
            if '"detection_result"' in error_str:
                print(f"   Column: detection_result must not be null")
                print(f"   💡 Retrying with default value 'pending'...")
                # We already set default above, so this shouldn't happen
        
        if "row-level security" in error_str.lower() or "403" in error_str:
            print(f"\n   🔐 RLS POLICY ERROR on detection_history table!")
            print(f"   The detection_history table also has RLS enabled.")
            print(f"\n   📋 TO FIX: Add this policy to detection_history table:")
            print(f"   Go to SQL Editor and run:")
            print(f"   ```sql")
            print(f"   CREATE POLICY \"Allow service role on detection_history\"")
            print(f"   ON detection_history")
            print(f"   FOR ALL")
            print(f"   TO service_role")
            print(f"   USING (true)")
            print(f"   WITH CHECK (true);")
            print(f"   ```\n")
        
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
