#!/bin/bash

# WhatsApp Bot Cleanup Script
# Removes unnecessary files before deployment

echo "🧹 Cleaning up WhatsApp bot folder..."
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# List files to be removed
echo "📋 Files to be removed:"
echo "  - app.py.backup"
echo "  - app.py.old"
echo "  - check_buckets.py"
echo "  - diagnose.py"
echo "  - advanced_diagnose.py"
echo "  - start_tunnel.py"
echo ""

read -p "⚠️  Proceed with cleanup? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Remove backup files
    if [ -f "app.py.backup" ]; then
        rm app.py.backup
        echo "✅ Removed app.py.backup"
    fi
    
    if [ -f "app.py.old" ]; then
        rm app.py.old
        echo "✅ Removed app.py.old"
    fi
    
    # Remove diagnostic scripts
    if [ -f "check_buckets.py" ]; then
        rm check_buckets.py
        echo "✅ Removed check_buckets.py"
    fi
    
    if [ -f "diagnose.py" ]; then
        rm diagnose.py
        echo "✅ Removed diagnose.py"
    fi
    
    if [ -f "advanced_diagnose.py" ]; then
        rm advanced_diagnose.py
        echo "✅ Removed advanced_diagnose.py"
    fi
    
    # Remove tunneling script
    if [ -f "start_tunnel.py" ]; then
        rm start_tunnel.py
        echo "✅ Removed start_tunnel.py"
    fi
    
    echo ""
    echo "✨ Cleanup complete!"
    echo ""
    echo "📦 Remaining core files:"
    ls -lh *.py 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'
    
    echo ""
    echo "📋 Next steps:"
    echo "  1. Create Procfile: echo 'web: gunicorn app:app' > Procfile"
    echo "  2. Test locally: python app.py"
    echo "  3. Commit changes: git add . && git commit -m 'Clean up for deployment'"
    echo "  4. Push to GitHub: git push origin main"
    echo "  5. Deploy to Render.com (see CLEANUP_AND_HOSTING.md)"
else
    echo "❌ Cleanup cancelled"
fi

