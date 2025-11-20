# 🔧 Fix: Supabase Client Error

## Error You're Seeing

```
❌ Error uploading to Supabase bucket 'image-uploads': 
Client.__init__() got an unexpected keyword argument 'proxy'
```

## Root Cause

Version incompatibility between `supabase-py` library versions. The newer version (2.22.2) has different initialization parameters.

## ✅ Solution

### Step 1: Stop the Flask App

In Terminal 1, press `Ctrl+C` to stop the running app.

### Step 2: Reinstall Supabase with Compatible Version

```bash
cd /home/lightdesk/Projects/AI-Website/whatsapp
source venv/bin/activate

# Uninstall current version
pip uninstall supabase supabase-auth supabase-functions supabase-storage3 -y

# Install compatible version
pip install supabase==2.9.0

# Verify installation
pip show supabase
```

### Step 3: Restart Flask App

```bash
python app.py
```

### Step 4: Test Again

Send an image to your WhatsApp bot - it should now upload successfully!

---

## Alternative: Use Updated Code

I've already updated the code to handle version compatibility issues. The changes:

1. **`storage_service.py`** - Added fallback initialization method
2. **`requirements.txt`** - Downgraded to compatible version

Just reinstall requirements and restart:

```bash
pip install -r requirements.txt
python app.py
```

---

## Expected Output After Fix

When you upload an image, you should see:

```
📤 Uploading to bucket: image-uploads, filename: ...
   File size: 611834 bytes
✅ Upload response: {...}
🔗 Public URL generated: https://...supabase.co/...
🤖 Running AI detection on image...
✅ AI detection complete: Authentic Human Content (92%)
💾 Storing metadata in detection_history table...
✅ Metadata stored successfully! Record ID: abc-123
Message sent to 917892055781: {...}
```

---

## Quick Commands

```bash
# Stop Flask (Ctrl+C in Terminal 1)

# Reinstall
cd /home/lightdesk/Projects/AI-Website/whatsapp
source venv/bin/activate
pip uninstall supabase -y
pip install supabase==2.9.0

# Restart
python app.py

# Test: Send image to WhatsApp bot
```

---

## If Still Not Working

### Check Supabase Bucket Exists

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Storage**
4. Verify these buckets exist:
   - `image-uploads`
   - `video-uploads`
   - `text-uploads`

### Check Bucket is Public

1. Click on `image-uploads` bucket
2. Go to **Configuration**
3. Make sure **Public bucket** is enabled

### Check RLS Policies

1. Go to **Policies** tab in the bucket
2. Should have a policy allowing uploads
3. Or disable RLS for testing

---

## Status

✅ **Code Updated** - `storage_service.py` now has fallback method  
✅ **Requirements Updated** - `requirements.txt` uses compatible version  
🔄 **Action Needed** - Reinstall requirements and restart Flask app

---

**After fixing, your bot will work perfectly! 🚀**

