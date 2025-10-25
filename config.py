"""
Configuration settings for WhatsApp Deepfake Detector Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WhatsApp Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "abc123")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Flask Configuration
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# File Type Mappings
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
        'mime_types': ['application/pdf', 'application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                      'text/plain', 'text/csv']
    }
}

# Bot Messages
WELCOME_MESSAGE = """👋 Hey there! Welcome to Deepfake Detector!

I can help you detect deepfakes in images and videos. Just send me:
📸 A photo
🎥 A video
📄 A document

And I'll analyze it for you!"""

HELP_MESSAGE = """💡 To detect deepfakes, please send an image, video, or document file.

Supported formats:
• Images: JPG, PNG, GIF, WebP
• Videos: MP4, MOV, AVI, MKV, WebM
• Documents: PDF, DOC, DOCX, TXT, CSV"""
