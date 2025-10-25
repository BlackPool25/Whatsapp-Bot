# API Documentation - WhatsApp Bot & Web Application

## Base URL
```
http://localhost:5000  (Development)
https://your-domain.com  (Production)
```

## Endpoints Overview

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/webhook` | GET | No | WhatsApp webhook verification |
| `/webhook` | POST | No | WhatsApp message handler |
| `/api/upload` | POST | Optional | Upload files from web app |
| `/api/history` | GET | Optional | Fetch detection history |
| `/api/history/<id>` | GET | Optional | Fetch specific record |
| `/api/session` | POST | No | Generate session ID |
| `/health` | GET | No | Health check |

---

## 1. WhatsApp Webhook Endpoints

### GET /webhook
**Purpose:** Webhook verification from Meta/WhatsApp

**Query Parameters:**
- `hub.verify_token` - Your verify token
- `hub.challenge` - Challenge string from Meta

**Response:** Returns challenge string if token matches

---

### POST /webhook
**Purpose:** Receives messages and media from WhatsApp users

**Request:** Automatic from WhatsApp API

**Supported Message Types:**
- Text messages (greeting and info)
- Image messages (jpg, jpeg, png, gif, webp, heic)
- Video messages (mp4, mov, avi, mkv, webm)
- Document messages (pdf, doc, docx, txt, csv)

**Behavior:**
- Files are downloaded from WhatsApp
- Automatically routed to correct bucket
- session_id = WhatsApp phone number
- user_id = NULL (anonymous)
- Reply sent to user with upload confirmation

---

## 2. Web Application API Endpoints

### POST /api/upload
**Purpose:** Upload files from web application

**Authentication:** 
- Optional: Bearer token (for logged-in users)
- If no token: Requires `session_id` or generates temporary one

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` (required) - The file to upload
- `session_id` (optional) - Session ID for anonymous users
- `user_id` (optional) - User ID (can be extracted from Bearer token)

**Headers:**
```
Authorization: Bearer <jwt_token>  (optional)
```

**Request Example (Authenticated User):**
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**Request Example (Anonymous User with Session):**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/video.mp4" \
  -F "session_id=temp_abc123def456"
```

**Request Example (Anonymous User without Session):**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@/path/to/document.pdf"
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_url": "https://your-project.supabase.co/storage/v1/object/public/image-uploads/user123_1234567890_abc123_image.jpg",
    "filename": "user123_1234567890_abc123_image.jpg",
    "file_type": "image",
    "bucket": "image-uploads",
    "size": 524288,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": null,
    "created_at": "2025-10-26T12:34:56.789Z"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No file provided"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Failed to upload file to storage"
}
```

---

### GET /api/history
**Purpose:** Fetch detection history with conditional logic

**Authentication:** Optional Bearer token

**Query Parameters:**
- `session_id` (optional) - Session ID for anonymous users

**Headers:**
```
Authorization: Bearer <jwt_token>  (optional)
```

**Query Logic:**

1. **Logged-in User (has Bearer token with valid user_id):**
   - Returns ALL records where `user_id` matches
   - Ignores `session_id` parameter
   - Example: User logs in → sees all their history from all sessions

2. **Anonymous User (no Bearer token but has session_id):**
   - Returns ONLY records where `user_id IS NULL` AND `session_id` matches
   - Example: Anonymous user → sees only files uploaded in this session

3. **No Auth and No Session:**
   - Returns error: "Session not found"

**Request Example (Authenticated User):**
```bash
curl -X GET http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Request Example (Anonymous User):**
```bash
curl -X GET "http://localhost:5000/api/history?session_id=temp_abc123def456"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "session_id": null,
      "file_url": "https://...",
      "filename": "user123_1234567890_abc123_image.jpg",
      "file_type": "image",
      "file_size": 524288,
      "file_extension": "jpg",
      "detection_result": null,
      "confidence_score": null,
      "is_file_available": true,
      "file_deleted_at": null,
      "created_at": "2025-10-26T12:34:56.789Z",
      "updated_at": "2025-10-26T12:34:56.789Z"
    }
  ],
  "count": 1
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Session not found. Please provide a valid session_id or authentication token."
}
```

---

### GET /api/history/<record_id>
**Purpose:** Fetch a specific detection record by ID

**Authentication:** Optional Bearer token

**Path Parameters:**
- `record_id` - UUID of the detection record

**Query Parameters:**
- `session_id` (optional) - Session ID for anonymous users

**Headers:**
```
Authorization: Bearer <jwt_token>  (optional)
```

**Authorization Logic:**
- If record has `user_id`: Must match authenticated user's ID
- If record has NO `user_id`: Must provide matching `session_id`

**Request Example:**
```bash
curl -X GET "http://localhost:5000/api/history/550e8400-e29b-41d4-a716-446655440000?session_id=temp_abc123def456"
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": null,
    "session_id": "temp_abc123def456",
    "file_url": "https://...",
    "filename": "temp_abc123_1234567890_xyz789_document.pdf",
    "file_type": "document",
    "file_size": 1048576,
    "file_extension": "pdf",
    "detection_result": null,
    "confidence_score": null,
    "is_file_available": true,
    "file_deleted_at": null,
    "created_at": "2025-10-26T12:34:56.789Z",
    "updated_at": "2025-10-26T12:34:56.789Z"
  }
}
```

**Response (403 Forbidden):**
```json
{
  "error": "Unauthorized access"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Record not found"
}
```

---

### POST /api/session
**Purpose:** Generate a new temporary session ID for anonymous users

**Authentication:** None required

**Request Example:**
```bash
curl -X POST http://localhost:5000/api/session
```

**Response (201 Created):**
```json
{
  "success": true,
  "session_id": "temp_abc123def456"
}
```

**Use Case:**
- Web app can call this on page load for anonymous users
- Store `session_id` in localStorage/sessionStorage
- Use it for subsequent uploads and history queries

---

### GET /health
**Purpose:** Health check endpoint

**Request Example:**
```bash
curl -X GET http://localhost:5000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "whatsapp-bot-deepfake-detector"
}
```

---

## File Routing Logic

Files are automatically routed to buckets based on extension:

| Extensions | Bucket | File Type |
|------------|--------|-----------|
| jpg, jpeg, png, gif, webp, heic | image-uploads | image |
| mp4, mov, avi, mkv, webm | video-uploads | video |
| pdf, doc, docx, txt, csv | text-uploads | document |

**Filename Format:**
```
{user_id || session_id}_{timestamp}_{random_id}_{original_filename}
```

**Examples:**
- `550e8400-e29b-41d4-a716-446655440000_1698336000_a1b2c3d4_photo.jpg`
- `temp_abc123def456_1698336000_x9y8z7w6_document.pdf`
- `+1234567890_1698336000_m5n6p7q8_video.mp4` (WhatsApp)

---

## User Scenarios

### Scenario 1: Logged-in Web User
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`
  },
  body: formData
});

// Fetch history (gets ALL user's records)
fetch('/api/history', {
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});
```

### Scenario 2: Anonymous Web User
```javascript
// Generate session on page load
const response = await fetch('/api/session', { method: 'POST' });
const { session_id } = await response.json();
localStorage.setItem('sessionId', session_id);

// Upload file with session_id
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('session_id', session_id);

fetch('/api/upload', {
  method: 'POST',
  body: formData
});

// Fetch history (gets only this session's records)
fetch(`/api/history?session_id=${session_id}`);
```

### Scenario 3: WhatsApp User
```
1. User sends image to WhatsApp bot
2. Bot receives webhook → downloads image
3. session_id = user's phone number
4. user_id = NULL
5. File uploaded to appropriate bucket
6. Record stored in detection_history
7. User receives confirmation message
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (missing parameters) |
| 403 | Forbidden (unauthorized access) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Environment Variables Required

```env
VERIFY_TOKEN=your_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:5000/health

# Create session
curl -X POST http://localhost:5000/api/session

# Upload file (anonymous)
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test.jpg" \
  -F "session_id=temp_test123"

# Get history (anonymous)
curl "http://localhost:5000/api/history?session_id=temp_test123"
```

### Using Postman

1. **Upload File:**
   - Method: POST
   - URL: `http://localhost:5000/api/upload`
   - Body: form-data
   - Add key "file" (type: File)
   - Add key "session_id" (type: Text)

2. **Get History:**
   - Method: GET
   - URL: `http://localhost:5000/api/history?session_id=your_session_id`
