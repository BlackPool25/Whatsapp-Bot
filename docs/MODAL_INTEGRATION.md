# WhatsApp Bot - Modal AI Integration

## ✅ Implementation Complete

The WhatsApp bot now uses the Modal-hosted EfficientFormer-S2V1 model for real-time image deepfake detection.

---

## 🎯 What Was Implemented

### 1. New Module: `modal_service.py`
- **Function**: `detect_image_ai(file_content, mime_type)` - Sends image to Modal API
- **Function**: `map_modal_response(modal_data)` - Converts Modal response to standard format
- **Function**: `format_detection_response(result, filename)` - Formats AI results for WhatsApp
- **Function**: `health_check()` - Tests Modal API connectivity

### 2. Updated: `message_handler.py`
- **Image messages** now trigger real AI detection via Modal
- **Video/document messages** still work (detection pending)
- **Results** are formatted and sent back to user
- **Database** stores AI detection results

### 3. Updated: `storage_service.py`
- **Enhanced** `store_detection_history()` to handle JSON detection results
- **Stores** model name (`EfficientFormer-S2V1 (Modal)`)
- **Saves** confidence scores and full detection data

### 4. Updated: `config.py`
- Added `MODAL_API_URL` configuration
- Added optional `MODAL_API_KEY` for secured endpoints

---

## 🚀 Setup Instructions

### Step 1: Add Environment Variables

Create or update `.env` file in the `whatsapp/` directory:

```env
# Existing variables
VERIFY_TOKEN=your_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Supabase (should already be set)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_key

# Modal AI - NEW
MODAL_API_URL=https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run
# MODAL_API_KEY=your_modal_api_key  # Optional
```

### Step 2: Verify Dependencies

All required packages are already in `requirements.txt`. If you need to reinstall:

```bash
cd whatsapp/
pip install -r requirements.txt
```

### Step 3: Test Modal Connection

Run the test script to verify Modal API is reachable:

```bash
cd whatsapp/
python modal_service.py
```

Expected output:
```
🧪 Testing Modal API connection...
Health check: ✅ Modal API is healthy (Device: cuda, CUDA: True)
```

### Step 4: Start the Bot

```bash
cd whatsapp/
python app.py
```

---

## 📱 How It Works

### User Flow

1. **User sends message**: "1" (to select Image mode)
2. **Bot responds**: "Great! Send me an image..."
3. **User sends image**: Any JPG/PNG/WebP image
4. **Bot processes**:
   - Downloads image from WhatsApp servers
   - Uploads to Supabase Storage (`image-uploads` bucket)
   - **NEW:** Sends to Modal API for AI detection
   - Receives detection result
   - Stores in database with results
   - Formats nice response
5. **User receives**: Detailed detection results with confidence score

### Technical Flow

```
WhatsApp Message (image)
    ↓
download_whatsapp_media() - Download from WhatsApp
    ↓
upload_to_supabase() - Store in Supabase
    ↓
detect_image_ai() - Send to Modal API [NEW]
    ↓
map_modal_response() - Parse Modal response [NEW]
    ↓
store_detection_history() - Save to database with AI results
    ↓
format_detection_response() - Format for WhatsApp [NEW]
    ↓
send_whatsapp_message() - Send back to user
```

---

## 📊 Detection Result Format

### Modal API Response (Raw)

```json
{
  "predictions": [
    {"label": "REAL", "score": 0.92},
    {"label": "AI", "score": 0.08}
  ],
  "top_prediction": "REAL",
  "confidence": 0.92
}
```

### Mapped Result (Internal)

```python
{
  "confidence": 92,           # 0-100 scale
  "isAI": False,              # Boolean
  "label": "Authentic Human Content",
  "emoji": "✅",
  "model": "EfficientFormer-S2V1 (Modal)",
  "raw_predictions": [...],
  "top_prediction": "REAL"
}
```

### WhatsApp Message (Formatted)

```
✅ *Detection Results*

📁 File: image_1234567890.jpg
🤖 Model: EfficientFormer-S2V1 (Modal)

━━━━━━━━━━━━━━━━━━

✅ *Authentic Human Content*

This content appears to be authentic human-created.

📊 *Confidence Score*
🟢 92% ██████████

📈 *Detailed Scores:*
   • REAL: 92%
   • AI: 8%

━━━━━━━━━━━━━━━━━━

💡 Type *start* to analyze another file!
```

---

## 🔧 Configuration Options

### Modal API URL

Default: `https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run`

To change:
```env
MODAL_API_URL=https://your-custom-modal-url.modal.run
```

### Modal API Key (Optional)

If you secure your Modal endpoint with authentication:

```env
MODAL_API_KEY=your_secret_api_key
```

The bot will automatically include this in the `Authorization` header.

### Timeout Settings

Default timeout: 30 seconds

To modify, edit `modal_service.py`:

```python
response = requests.post(url, headers=headers, json=payload, timeout=60)  # 60 seconds
```

---

## 🐛 Error Handling

### Scenario 1: Modal API Unreachable

**What happens:**
- Image uploads to Supabase successfully
- Detection result stored as `{"status": "failed", "error": "..."}`
- User receives fallback message: "File saved successfully, but AI detection unavailable"

**User experience:**
```
🖼 Image uploaded successfully!

📁 File: image_1234567890.jpg
📊 Type: image
💾 Size: 45,678 bytes

⚠️ AI detection unavailable at the moment.
📝 File saved successfully.

💡 Type *start* to analyze another file!
```

### Scenario 2: Modal API Timeout

**What happens:**
- Request times out after 30 seconds
- Catches `requests.exceptions.Timeout`
- Same fallback as Scenario 1

### Scenario 3: Invalid Image Format

**What happens:**
- Modal API returns 400 error
- Bot logs the error
- User receives error message

---

## 📈 Database Schema

Detection results are stored in `detection_history` table:

```sql
{
  id: uuid,
  user_id: uuid (nullable),
  session_id: text (phone number),
  file_url: text,
  filename: text,
  file_type: text ("image"),
  file_size: integer,
  file_extension: text ("jpg", "png", etc.),
  detection_result: jsonb,  -- {confidence, isAI, label, model}
  confidence_score: float,  -- 0-100
  model_used: text,         -- "EfficientFormer-S2V1 (Modal)"
  is_file_available: boolean,
  created_at: timestamp
}
```

---

## 🧪 Testing Guide

### Test Case 1: Real Human Image

1. Send "1" to bot
2. Upload a photo you took yourself
3. Expected: High confidence "Authentic Human Content"

### Test Case 2: AI-Generated Image

1. Send "1" to bot
2. Upload an AI-generated image (e.g., from Midjourney, DALL-E)
3. Expected: High confidence "AI-Generated Content Detected"

### Test Case 3: Video Upload

1. Send "2" to bot
2. Upload a video
3. Expected: Video saved, but "AI detection coming soon" message

### Test Case 4: Multiple Images

1. Upload 3 different images in sequence
2. Expected: Each gets analyzed independently with correct results

### Test Case 5: Modal API Down

1. Temporarily change `MODAL_API_URL` to invalid URL in `.env`
2. Restart bot
3. Upload image
4. Expected: Fallback message, file still saved

---

## 💰 Cost Considerations

### Modal GPU Usage

- **Cost**: ~$0.60/hour when running (T4 GPU)
- **Auto-scaling**: Scales to zero when idle
- **Typical usage**: 2-3 seconds per image
- **Cold start**: 10-15 seconds (first request after idle)

### Optimization Tips

1. **Modal keep-warm**: Already configured to minimize cold starts
2. **Batch processing**: If you get multiple images, Modal handles them efficiently
3. **Monitor usage**: Check Modal dashboard for actual costs

### Estimated Costs (Example)

- 100 images/day = ~5 minutes GPU time = $0.05/day = $1.50/month
- 1000 images/day = ~50 minutes GPU time = $0.50/day = $15/month

---

## 🔒 Security Considerations

### Current Setup (Development/Testing)

- Modal API is publicly accessible
- No authentication required on Modal endpoint
- Good for testing and low-volume usage

### Production Recommendations

1. **Enable Modal API Key**:
   ```env
   MODAL_API_KEY=your_secure_random_key_here
   ```
   Update Modal app to require this key.

2. **Rate Limiting**:
   Add rate limiting per phone number to prevent abuse.

3. **Whitelist Phone Numbers** (optional):
   Only allow specific phone numbers to use the bot.

4. **Monitor Usage**:
   Set up alerts in Modal dashboard for unusual activity.

---

## 🆚 Differences from Web App

### Similarities

- Both use same Modal API endpoint
- Same detection model (EfficientFormer-S2V1)
- Same confidence scoring
- Same database structure

### Differences

| Feature | Web App | WhatsApp Bot |
|---------|---------|--------------|
| **Auth** | Supabase Auth (email/password) | Phone number as session_id |
| **File Upload** | Direct to Supabase from browser | WhatsApp → Server → Supabase |
| **User ID** | UUID from auth | Phone number |
| **Response Format** | JSON API | Formatted WhatsApp message |
| **Detection Trigger** | `/api/detect` endpoint | Inline in message handler |

---

## 📚 File Structure

```
whatsapp/
├── app.py                    # Main Flask app (unchanged)
├── message_handler.py        # [UPDATED] Added AI detection
├── storage_service.py        # [UPDATED] Enhanced DB storage
├── modal_service.py          # [NEW] Modal API integration
├── whatsapp_service.py       # (unchanged)
├── config.py                 # [UPDATED] Added Modal config
├── requirements.txt          # (unchanged - has requests)
└── docs/
    └── MODAL_INTEGRATION.md  # [NEW] This file
```

---

## 🔄 Next Steps

### For Text Detection

1. Deploy text detection model to Modal
2. Update `message_handler.py` to call Modal for text
3. Add text-specific formatting

### For Video Detection

1. Deploy video detection model to Modal (may need different endpoint)
2. Handle video frame extraction
3. Update message handler for video

### Production Deployment

1. Deploy to cloud server (AWS, GCP, Heroku, etc.)
2. Set up Grok webhook with public URL
3. Add environment variables to production
4. Test thoroughly
5. Monitor logs and costs

---

## 📞 Troubleshooting

### Issue: "Modal API is not reachable"

**Check:**
1. Is `MODAL_API_URL` set correctly in `.env`?
2. Is Modal app deployed and running?
3. Run `python modal_service.py` to test connectivity

**Solution:**
```bash
# Test Modal API directly
curl https://blackpool25--ai-vs-real-detector-fastapi-app.modal.run/health
```

### Issue: Images upload but no AI detection

**Check:**
1. Look at bot console output - should see "🤖 Running AI detection on image..."
2. Check for error messages in console
3. Verify Modal API URL is correct

**Debug:**
```bash
# In Python console
from modal_service import health_check
is_healthy, msg = health_check()
print(f"Healthy: {is_healthy}, Message: {msg}")
```

### Issue: "Detection result is null in database"

**Cause:** Modal API call failed but file upload succeeded

**Solution:** This is expected behavior - file is saved even if detection fails

---

## ✅ Verification Checklist

Before considering this complete:

- [ ] `MODAL_API_URL` added to `.env` in `whatsapp/` folder
- [ ] Bot restarts without errors
- [ ] Modal API health check passes
- [ ] Test image upload triggers AI detection
- [ ] Detection results appear in WhatsApp message
- [ ] Database stores detection results correctly
- [ ] Video/text modes still work (with "coming soon" message)
- [ ] Error handling works when Modal is unreachable

---

**Status**: ✅ Implementation Complete  
**Last Updated**: November 19, 2025  
**Ready for Testing**: Yes

Test with: `python app.py` in the `whatsapp/` directory!

