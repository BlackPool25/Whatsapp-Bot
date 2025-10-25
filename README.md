# WhatsApp Bot - Deepfake Detector

A WhatsApp bot that accepts file uploads (images, videos, documents) from both authenticated and anonymous users, stores them in Supabase buckets, and tracks detection history.

## Features

- ✅ Support for authenticated and anonymous users
- ✅ Automatic file type detection and routing to appropriate buckets
- ✅ Collision-free filename generation
- ✅ Image uploads → `image-uploads` bucket
- ✅ Video uploads → `video-uploads` bucket
- ✅ Document uploads → `text-uploads` bucket
- ✅ Metadata storage in `detection_history` table
- ✅ Automatic file cleanup via cron job (every 30 minutes)

## Prerequisites

- Python 3.8+
- Supabase account
- WhatsApp Business API access (Meta Developer account)
- ngrok or similar tunneling service for local development

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd whatsapp
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env` (or update the existing `.env`)
   - Update the following variables:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
     WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
     WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
     VERIFY_TOKEN=your_custom_verify_token
     ```

## Supabase Setup

### 1. Create Storage Buckets

Create three public buckets in your Supabase project:
- `image-uploads`
- `video-uploads`
- `text-uploads`

### 2. Create Database Table

Run the SQL script in `database_schema.sql` to create the `detection_history` table.

### 3. Set up Bucket Policies

Ensure all three buckets are set to **Public** for read access.

## WhatsApp Business API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create or select an app with WhatsApp Business API
3. Get your:
   - Access Token
   - Phone Number ID
   - Create a custom Verify Token
4. Set up webhook:
   - URL: `https://your-domain.com/webhook`
   - Verify Token: (same as in your `.env`)
   - Subscribe to `messages` events

## Running the Application

### Development

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Using ngrok (for local development)

```bash
ngrok http 5000
```

Use the ngrok URL as your webhook URL in the Meta Developer console.

### Production

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## File Upload Flow

1. **User sends file** via WhatsApp (image, video, or document)
2. **Bot receives webhook** from WhatsApp API
3. **File is downloaded** from WhatsApp servers
4. **File type is detected** based on extension/MIME type
5. **Unique filename is generated**: `{userId}_{timestamp}_{randomId}_{originalFilename}`
6. **File is uploaded** to appropriate Supabase bucket
7. **Metadata is stored** in `detection_history` table
8. **User receives confirmation** with file details

## Anonymous User Handling

For users who are not logged in:
- A consistent anonymous ID is generated using: `anon_{uuid5(phone_number)[:16]}`
- This ensures the same user gets the same anonymous ID across sessions
- Files are still tracked and stored properly

## File Type Routing

| File Extension | Bucket | File Type |
|----------------|--------|-----------|
| jpg, jpeg, png, gif, webp, heic | image-uploads | image |
| mp4, mov, avi, mkv, webm | video-uploads | video |
| pdf, doc, docx, txt, csv | text-uploads | document |

## Database Schema

The `detection_history` table stores:
- `id` (uuid, primary key)
- `user_id` (uuid or anonymous ID)
- `file_url` (text)
- `filename` (text)
- `file_type` (text)
- `file_size` (bigint)
- `file_extension` (text)
- `is_file_available` (boolean)
- `file_deleted_at` (timestamp)
- `created_at` (timestamp)

## Cron Job for File Cleanup

Set up a cron job to run every 30 minutes:

```bash
*/30 * * * * curl -X POST https://your-domain.com/cleanup-files
```

(Note: You'll need to implement the `/cleanup-files` endpoint separately)

## API Endpoints

### `GET /webhook`
Webhook verification for WhatsApp

### `POST /webhook`
Receives messages and media from WhatsApp

## Error Handling

The application includes comprehensive error handling for:
- Failed file downloads from WhatsApp
- Failed uploads to Supabase
- Database insertion errors
- Invalid file types
- Missing media IDs

## Security Considerations

- Store sensitive credentials in `.env` file (never commit to Git)
- Use HTTPS in production
- Validate webhook requests
- Implement rate limiting
- Sanitize filenames to prevent path traversal

## Troubleshooting

**Issue: "Import could not be resolved"**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`

**Issue: "Failed to upload file to storage"**
- Verify your Supabase credentials
- Check if buckets exist and are public
- Ensure bucket names match exactly

**Issue: "No media ID found"**
- Check WhatsApp webhook configuration
- Verify access token is valid
- Ensure message type is supported

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
