# 🗄️ How to Create Supabase Storage Buckets

## ❌ Error: "Failed to upload file to storage"

**Cause:** The storage buckets don't exist in your Supabase project yet.

**Fix:** Create 3 storage buckets manually in Supabase Dashboard.

---

## 📝 Step-by-Step Instructions:

### **Step 1: Go to Supabase Dashboard**

Open this link in your browser:
```
https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets
```

Or navigate manually:
1. Go to https://supabase.com/dashboard
2. Click on your project: `cjkcwycnetdhumtqthuk`
3. Click "Storage" in the left sidebar
4. Click on "Buckets" tab

---

### **Step 2: Create First Bucket (image-uploads)**

1. Click the **"New bucket"** or **"Create bucket"** button

2. Fill in the form:
   ```
   Name: image-uploads
   ☑ Public bucket (MUST be checked!)
   ```

3. Click **"Create bucket"**

---

### **Step 3: Create Second Bucket (video-uploads)**

1. Click **"New bucket"** again

2. Fill in:
   ```
   Name: video-uploads
   ☑ Public bucket (MUST be checked!)
   ```

3. Click **"Create bucket"**

---

### **Step 4: Create Third Bucket (text-uploads)**

1. Click **"New bucket"** again

2. Fill in:
   ```
   Name: text-uploads
   ☑ Public bucket (MUST be checked!)
   ```

3. Click **"Create bucket"**

---

### **Step 5: Verify Buckets**

You should now see 3 buckets in your Storage dashboard:
- ✅ image-uploads (Public)
- ✅ video-uploads (Public)
- ✅ text-uploads (Public)

---

## 🧪 Test After Creating Buckets

1. **Restart your Flask app** (to clear any cached errors):
   ```bash
   pkill -f "python.*app.py"
   /home/lightdesk/Projects/whatsapp/venv/bin/python app.py
   ```

2. **Send an image** to your WhatsApp bot from your phone

3. **Check the Flask terminal** - you should see:
   ```
   📤 Uploading to bucket: image-uploads, filename: ...
   ✅ Upload response: ...
   🔗 Public URL generated: ...
   ```

4. **Bot should reply** with success message!

---

## ⚙️ Bucket Configuration Details

### **Why "Public bucket"?**
- Public buckets allow files to have public URLs
- Your bot needs to share file URLs
- Files are still secure (long random filenames)

### **Optional Settings:**
You can also configure:
- **File size limit**: Default is fine (100MB)
- **Allowed MIME types**: Leave empty for now
- **RLS policies**: Not needed for basic usage

---

## 🔧 Troubleshooting

### If you still get errors after creating buckets:

**1. Check bucket names are EXACTLY:**
   - `image-uploads` (not image_uploads or imageUploads)
   - `video-uploads` (not video_uploads)
   - `text-uploads` (not text_uploads)

**2. Verify buckets are PUBLIC:**
   - In Storage dashboard, each bucket should show "Public: Yes"
   - If not, click bucket → Settings → Make public

**3. Check Supabase URL and Key:**
   - Make sure .env file has correct values
   - Try copying them again from Supabase Dashboard → Settings → API

**4. Restart everything:**
   ```bash
   # Stop Flask app
   pkill -f "python.*app.py"
   
   # Start it again
   /home/lightdesk/Projects/whatsapp/venv/bin/python app.py
   ```

---

## 📸 What Your Dashboard Should Look Like

After creating all buckets, your Storage page should show:

```
📦 Buckets (3)

Name             Public    Objects    Size
────────────────────────────────────────────
image-uploads    Yes       0          0 B
video-uploads    Yes       0          0 B
text-uploads     Yes       0          0 B
```

---

## ✅ Quick Checklist

- [ ] Opened Supabase Dashboard
- [ ] Navigated to Storage → Buckets
- [ ] Created `image-uploads` bucket (Public ✓)
- [ ] Created `video-uploads` bucket (Public ✓)
- [ ] Created `text-uploads` bucket (Public ✓)
- [ ] All 3 buckets show as Public
- [ ] Restarted Flask app
- [ ] Tested sending an image to bot

---

**Once you've created the buckets, your bot will be able to upload and store images, videos, and documents!**
