"""
Supabase Storage Bucket Setup Guide and Diagnostic
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 80)
print("🗄️  SUPABASE STORAGE BUCKET DIAGNOSTIC")
print("=" * 80)

required_buckets = {
    'image-uploads': 'For storing images (JPG, PNG, GIF, WebP, HEIC)',
    'video-uploads': 'For storing videos (MP4, MOV, AVI, MKV, WebM)',
    'text-uploads': 'For storing documents (PDF, DOC, DOCX, TXT, CSV)'
}

print(f"\n📡 Connecting to Supabase...")
print(f"URL: {SUPABASE_URL}")

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected successfully!")
    
    print(f"\n🔍 Checking for required storage buckets...")
    print("-" * 80)
    
    # Get list of buckets
    try:
        buckets = client.storage.list_buckets()
        existing_bucket_names = [bucket.name for bucket in buckets] if buckets else []
        
        print(f"\n📦 Existing buckets found: {len(existing_bucket_names)}")
        for bucket in existing_bucket_names:
            print(f"   ✅ {bucket}")
        
        print(f"\n📋 Required buckets for WhatsApp bot:")
        print("-" * 80)
        
        missing_buckets = []
        for bucket_name, description in required_buckets.items():
            if bucket_name in existing_bucket_names:
                print(f"✅ {bucket_name:<20} - {description}")
            else:
                print(f"❌ {bucket_name:<20} - {description} (MISSING)")
                missing_buckets.append(bucket_name)
        
        if missing_buckets:
            print("\n" + "=" * 80)
            print("⚠️  MISSING BUCKETS DETECTED!")
            print("=" * 80)
            print(f"\nYou need to create these buckets: {', '.join(missing_buckets)}")
            print("\n📝 HOW TO CREATE BUCKETS IN SUPABASE:")
            print("-" * 80)
            print("""
1. Go to your Supabase Dashboard:
   → https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk

2. Click on "Storage" in the left sidebar

3. Click "Create a new bucket" button

4. For EACH missing bucket, do:
   
   Bucket Name: image-uploads (or video-uploads, text-uploads)
   ☑ Public bucket (checked)
   File size limit: 100 MB (or more if needed)
   Allowed MIME types: Leave empty (allow all) or specify:
      - image-uploads: image/jpeg, image/png, image/gif, image/webp
      - video-uploads: video/mp4, video/quicktime, video/webm
      - text-uploads: application/pdf, text/plain, application/msword
   
   Click "Create bucket"

5. Repeat for all missing buckets

6. IMPORTANT: Make sure "Public bucket" is CHECKED
   (This allows files to have public URLs)
            """)
            
            print("\n🔗 Quick Link:")
            print(f"   https://supabase.com/dashboard/project/cjkcwycnetdhumtqthuk/storage/buckets")
            
        else:
            print("\n" + "=" * 80)
            print("✅ ALL REQUIRED BUCKETS EXIST!")
            print("=" * 80)
            print("\nYour storage is properly configured.")
            
            # Test upload to each bucket
            print("\n🧪 Testing upload to each bucket...")
            print("-" * 80)
            
            test_content = b"test file content"
            test_results = {}
            
            for bucket_name in required_buckets.keys():
                try:
                    test_filename = f"test_{int(time.time())}.txt"
                    client.storage.from_(bucket_name).upload(
                        path=test_filename,
                        file=test_content,
                        file_options={"content-type": "text/plain"}
                    )
                    
                    # Try to get public URL
                    public_url = client.storage.from_(bucket_name).get_public_url(test_filename)
                    
                    # Delete test file
                    client.storage.from_(bucket_name).remove([test_filename])
                    
                    print(f"✅ {bucket_name:<20} - Upload test successful")
                    test_results[bucket_name] = True
                    
                except Exception as e:
                    print(f"❌ {bucket_name:<20} - Upload test failed: {e}")
                    test_results[bucket_name] = False
            
            if all(test_results.values()):
                print("\n✅ All buckets are working correctly!")
            else:
                print("\n⚠️  Some buckets have issues. Check permissions.")
                
    except Exception as e:
        print(f"❌ Error listing buckets: {e}")
        print("\nPossible issues:")
        print("1. SUPABASE_KEY might not have storage permissions")
        print("2. No buckets exist yet - you need to create them")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("\nCheck your .env file:")
    print(f"SUPABASE_URL={SUPABASE_URL}")
    print(f"SUPABASE_KEY={'*' * 20}...")

print("\n" + "=" * 80)
print("📚 ADDITIONAL NOTES:")
print("=" * 80)
print("""
- Buckets must be PUBLIC for the bot to generate accessible URLs
- Each bucket can have size limits (default 100MB is fine)
- You can set up RLS (Row Level Security) policies later for more control
- Make sure your Supabase project has enough storage quota
""")

print("=" * 80)

import time
