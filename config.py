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

# Modal AI Configuration
MODAL_API_URL = os.getenv("MODAL_API_URL", "https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run")
MODAL_API_KEY = os.getenv("MODAL_API_KEY")  # Optional, for secured endpoints

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
WELCOME_MESSAGE = """👋 Hey there! Welcome to *Deepfake Detector Bot*!

I can help you detect deepfakes and AI-generated content. 

*Please choose what you'd like to analyze:*

1️⃣ Send *1* for Image Analysis 🖼
2️⃣ Send *2* for Video Analysis 🎥
3️⃣ Send *3* for Text Analysis 📝

Just reply with the number of your choice!"""

HELP_MESSAGE = """💡 *How to use this bot:*

*Step 1:* Choose your analysis type
• Send *1* for Image
• Send *2* for Video  
• Send *3* for Text

*Step 2:* Send your content
• After choosing, send the image/video/text you want analyzed

*Supported formats:*
📸 Images: JPG, PNG, GIF, WebP
🎥 Videos: MP4, MOV, AVI, MKV, WebM
📝 Text: Any text message

Type *start* or *hi* to begin again!"""
