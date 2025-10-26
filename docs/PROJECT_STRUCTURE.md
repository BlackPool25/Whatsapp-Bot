# WhatsApp Deepfake Detector Bot

A Flask-based WhatsApp bot that detects deepfakes in images and videos.

## 📁 Project Structure

The project has been reorganized into a modular structure for better maintainability:

```
whatsapp/
├── app.py                    # Main Flask application (webhook & API endpoints)
├── config.py                 # Configuration and constants
├── whatsapp_service.py       # WhatsApp Cloud API interactions
├── storage_service.py        # Supabase storage and database operations
├── message_handler.py        # Message processing and routing logic
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── database_schema.sql       # Database schema
└── API_DOCUMENTATION.md      # API documentation
```

## 🔧 Module Breakdown

### **app.py** (Main Application)
- Flask app initialization
- Webhook endpoints (`/webhook`)
- Web API endpoints (`/api/*`)
- Health check endpoint (`/health`)

### **config.py** (Configuration)
- Environment variables loading
- WhatsApp API credentials
- Supabase configuration
- File type mappings
- Bot messages (welcome, help)

### **whatsapp_service.py** (WhatsApp API)
- `send_whatsapp_message()` - Send messages to users
- `download_whatsapp_media()` - Download media from WhatsApp
- `mark_message_as_read()` - Mark messages as read

### **storage_service.py** (Database & Storage)
- `get_supabase_client()` - Get Supabase client instance
- `upload_to_supabase()` - Upload files to storage buckets
- `store_detection_history()` - Save detection records
- `get_file_extension()` - Extract file extensions
- `determine_file_type_and_bucket()` - Route files to correct buckets
- `generate_unique_filename()` - Create unique filenames
- `get_user_from_token()` - JWT token verification

### **message_handler.py** (Message Processing)
- `process_whatsapp_message()` - Main message router
- `handle_text_message()` - Process text messages
- `handle_media_message()` - Process images, videos, documents
- `format_media_response()` - Create response messages
- User greeting management

## ✨ Key Improvements

### 1. **Modular Architecture**
- Separated concerns into focused modules
- Easier to test and maintain
- Better code organization

### 2. **Always Sends Initial Greeting**
- Bot now greets users on their first interaction, regardless of message type
- Tracks greeted users to avoid duplicate greetings
- Provides helpful instructions immediately

### 3. **Enhanced Message Handling**
- Processes all message types: text, image, video, document
- Always responds with appropriate messages
- Better error handling and user feedback

### 4. **Improved Webhook Logic**
- Properly extracts messages from webhook payload
- Marks messages as read
- Always returns 200 OK to acknowledge receipt
- Comprehensive error handling

## 🚀 Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using the virtual environment:

```bash
/home/lightdesk/Projects/whatsapp/venv/bin/python -m pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
# WhatsApp Cloud API
VERIFY_TOKEN=your_verify_token_here
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

### 3. Run the Application

```bash
python app.py
```

Or with the virtual environment:

```bash
/home/lightdesk/Projects/whatsapp/venv/bin/python app.py
```

The bot will start on `http://0.0.0.0:5000`

## 📱 Bot Features

### **Automatic Greetings**
- Users receive a welcome message on first contact
- Helps users understand bot capabilities
- Works for any message type (text, media, etc.)

### **Supported Message Types**

#### Text Messages
- Responds with welcome message for new users
- Provides help for commands like "hi", "hello", "help"
- Default response with instructions for other text

#### Media Messages
- **Images**: JPG, PNG, GIF, WebP, HEIC
- **Videos**: MP4, MOV, AVI, MKV, WebM
- **Documents**: PDF, DOC, DOCX, TXT, CSV

### **Response Flow**
1. User sends message → Bot receives via webhook
2. Bot greets new users automatically
3. Bot processes the message type
4. Bot uploads media to Supabase (if applicable)
5. Bot stores detection history
6. Bot sends confirmation with file details

## 🔍 API Endpoints

### Webhook
- **GET** `/webhook` - Webhook verification
- **POST** `/webhook` - Receive WhatsApp messages

### Web API
- **POST** `/api/upload` - Upload files from web app
- **GET** `/api/history` - Get detection history
- **GET** `/api/history/<record_id>` - Get specific record
- **POST** `/api/session` - Generate session ID
- **GET** `/health` - Health check

## 🛠 Troubleshooting

### Bot not responding?
1. Check webhook is properly configured in Meta Developer Console
2. Verify VERIFY_TOKEN matches in both .env and Meta settings
3. Ensure ACCESS_TOKEN and PHONE_NUMBER_ID are correct
4. Check application logs for errors

### Media upload failures?
1. Verify Supabase credentials (URL and KEY)
2. Check bucket permissions in Supabase dashboard
3. Ensure buckets exist: `image-uploads`, `video-uploads`, `text-uploads`

### First message not greeting?
- Fixed! The bot now always sends a greeting to new users, regardless of message type.

## 📝 Development

### Running in Development
```bash
python app.py
```
- Debug mode enabled by default
- Auto-reloads on code changes

### Running in Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- Use Gunicorn for production
- Adjust worker count based on load

## 🎯 Next Steps

1. Implement actual deepfake detection logic
2. Add support for more file types
3. Implement rate limiting
4. Add caching for frequently accessed data
5. Set up monitoring and logging
6. Add unit tests

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Keep modules focused and single-purpose
4. Test your changes
5. Submit a pull request

## 📞 Support

For issues or questions:
- Check the API_DOCUMENTATION.md file
- Review the code comments
- Check application logs
- Open an issue on GitHub
