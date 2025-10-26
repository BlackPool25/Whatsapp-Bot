# Fix Supabase Row-Level Security (RLS) Error

## Error You're Seeing:
```
❌ Error: new row violates row-level security policy
Status: 403 Unauthorized
```

## What This Means:
Your Supabase storage buckets have Row-Level Security (RLS) enabled. The RLS policy requires authenticated users and specific folder structure.

## ⚠️ **CRITICAL: Check Your Supabase Key First!**

Your `.env` file should use the **service_role** key (NOT the anon key):

```bash
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS...  # This should be service_role key
```

**To find your service_role key:**
1. Go to: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/settings/api
2. Look for **"service_role"** key (NOT "anon" key)
3. Copy the full key
4. Update your `.env` file with `SUPABASE_KEY=<service_role_key>`
5. Restart your bot

**Service role key bypasses RLS automatically!** If you're still getting RLS errors after using service_role key, continue with the fixes below.

## How to Fix:

### **Option 1: Make Buckets Public (Recommended for WhatsApp Bot)**

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets

2. For **each bucket** (image-uploads, video-uploads, text-uploads):
   - Click on the bucket name
   - Click the **"Configuration"** tab
   - Toggle **"Public bucket"** to ON
   - Click **"Save"**

### **Option 2: Update RLS Policy for Service Role**

Your current policy requires authenticated users and folder structure:
```sql
(auth.role() = 'authenticated') AND 
(bucket_id = 'text-uploads') AND 
((storage.foldername(name))[1] = auth.uid())
```

**Update each bucket's policy to allow service role:**

1. Go to: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets

2. For each bucket (image-uploads, video-uploads, text-uploads):
   - Click on the bucket name
   - Click **"Policies"** tab
   - Find your existing INSERT/SELECT policies
   - Edit them to include service role:

**For INSERT (Upload):**
```sql
(
  (auth.role() = 'authenticated' AND 
   bucket_id = 'image-uploads' AND 
   (storage.foldername(name))[1] = auth.uid()::text)
  OR
  (auth.role() = 'service_role')
)
```

**For SELECT (Download):**
```sql
(
  (auth.role() = 'authenticated' AND 
   bucket_id = 'image-uploads' AND 
   (storage.foldername(name))[1] = auth.uid()::text)
  OR
  (auth.role() = 'service_role')
  OR
  (bucket_id = 'image-uploads')  -- Allow public downloads
)
```

**Repeat for all buckets**, changing `'image-uploads'` to `'video-uploads'` and `'text-uploads'` accordingly.

### **Option 3: Simplest Fix - Add Service Role Policy**

Instead of modifying existing policies, add a new one:

1. Go to SQL Editor: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/sql/new

2. Run this SQL to allow service role uploads:

```sql
-- Allow service role to upload to all storage buckets
CREATE POLICY "Allow service role uploads to image-uploads"
ON storage.objects
FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'image-uploads');

CREATE POLICY "Allow service role uploads to video-uploads"
ON storage.objects
FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'video-uploads');

CREATE POLICY "Allow service role uploads to text-uploads"
ON storage.objects
FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'text-uploads');

-- Allow service role to read from all buckets
CREATE POLICY "Allow service role reads from image-uploads"
ON storage.objects
FOR SELECT
TO service_role
USING (bucket_id = 'image-uploads');

CREATE POLICY "Allow service role reads from video-uploads"
ON storage.objects
FOR SELECT
TO service_role
USING (bucket_id = 'video-uploads');

CREATE POLICY "Allow service role reads from text-uploads"
ON storage.objects
FOR SELECT
TO service_role
USING (bucket_id = 'text-uploads');
```

3. Click **"Run"**

### **Option 4: Disable RLS (Quick but less secure)**

1. Go to SQL Editor: https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/sql/new

2. Run this SQL for each bucket:
```sql
-- For image-uploads bucket
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- Make buckets public
UPDATE storage.buckets 
SET public = true 
WHERE name IN ('image-uploads', 'video-uploads', 'text-uploads');
```

## Test After Fixing:
1. Send "hi" to your WhatsApp bot
2. Choose option 1 (Image)
3. Send an image
4. Should upload successfully! ✅

## Current Bucket Names:
- `image-uploads` - for images
- `video-uploads` - for videos
- `text-uploads` - for documents/text files

---

**Note**: For a production WhatsApp bot, Option 1 (Public buckets) is typically the best choice since uploads come from your bot's service account, not end users.
