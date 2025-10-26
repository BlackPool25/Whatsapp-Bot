# WhatsApp Bot Flow Diagram

## Message Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER SENDS MESSAGE                       │
│                    (Text, Image, Video, Document)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WhatsApp Cloud API                            │
│                   Sends Webhook to Bot                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     app.py: /webhook                             │
│                   Receives POST request                          │
│                   Extracts message data                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│             message_handler.py: process_whatsapp_message()       │
│                                                                  │
│    ┌────────────────────────────────────────────────┐          │
│    │ 1. Check if user has been greeted              │          │
│    │ 2. If not, mark as greeted                     │          │
│    │ 3. Route to appropriate handler                │          │
│    └────────────────────────────────────────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
┌──────────────────────┐         ┌──────────────────────────┐
│   TEXT MESSAGE       │         │    MEDIA MESSAGE         │
│                      │         │  (Image/Video/Document)  │
│  handle_text_message │         │  handle_media_message    │
│                      │         │                          │
│  - Check for         │         │  - Download from         │
│    commands          │         │    WhatsApp API          │
│  - Return response   │         │  - Upload to Supabase    │
│                      │         │  - Store in database     │
│                      │         │  - Return response       │
└──────────┬───────────┘         └────────────┬─────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   whatsapp_service.py               │
        │   send_whatsapp_message()           │
        │                                     │
        │   Sends reply to user via           │
        │   WhatsApp Cloud API                │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   User receives response            │
        │   - Welcome message (if first time) │
        │   - Text confirmation               │
        │   - Media upload confirmation       │
        └─────────────────────────────────────┘
```

## Module Dependencies

```
app.py
  │
  ├─> config.py
  │     └─> Loads environment variables
  │
  ├─> whatsapp_service.py
  │     └─> Uses WhatsApp Cloud API
  │
  ├─> storage_service.py
  │     ├─> Uses Supabase client
  │     └─> Uses config.py
  │
  └─> message_handler.py
        ├─> Uses whatsapp_service.py
        ├─> Uses storage_service.py
        └─> Uses config.py
```

## File Upload Flow (Media Messages)

```
1. User sends image/video/document
   │
   ▼
2. WhatsApp Cloud API → Webhook → app.py
   │
   ▼
3. message_handler.py extracts media ID
   │
   ▼
4. whatsapp_service.py downloads media
   │
   ▼
5. storage_service.py:
   ├─> Determines file type (image/video/document)
   ├─> Generates unique filename
   ├─> Uploads to appropriate Supabase bucket
   │   ├─> image-uploads/
   │   ├─> video-uploads/
   │   └─> text-uploads/
   │
   ▼
6. storage_service.py stores metadata
   └─> detection_history table:
       ├─ file_url
       ├─ filename
       ├─ file_type
       ├─ file_size
       ├─ session_id (phone number)
       └─ user_id (if authenticated)
   │
   ▼
7. Bot sends confirmation to user
   └─> "Image uploaded successfully! Analyzing..."
```

## Key Features

### ✅ Always Greets New Users
- Bot tracks greeted users in memory
- First message always includes welcome message
- Works for ANY message type (text or media)

### ✅ Comprehensive Error Handling
- Try-catch blocks in all handlers
- Detailed error logging
- User-friendly error messages
- Always returns 200 OK to WhatsApp

### ✅ Modular Design
- Each module has single responsibility
- Easy to test and debug
- Clean imports and dependencies
- Reusable functions

### ✅ Smart File Handling
- Automatic file type detection
- Unique filename generation
- Appropriate bucket routing
- Metadata tracking
