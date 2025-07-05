#!/bin/bash

echo "🔍 Checking Vercel Deployment Status"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Run this from the project root."
    exit 1
fi

echo "✅ Found vercel.json configuration"

# Check if orchestration/main.py exists
if [ ! -f "orchestration/main.py" ]; then
    echo "❌ Error: orchestration/main.py not found"
    exit 1
fi

echo "✅ Found orchestration/main.py"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo "✅ Found requirements.txt"

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies are available"
else
    echo "⚠️  Python dependencies may need installation"
fi

# Test the FastAPI app import
echo "🐍 Testing FastAPI app import..."
cd orchestration
python3 -c "from main import app; print('✅ FastAPI app imported successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ FastAPI app can be imported"
else
    echo "❌ Error importing FastAPI app"
fi
cd ..

echo ""
echo "🚀 Deployment Checklist:"
echo "- ✅ vercel.json configuration exists"
echo "- ✅ orchestration/main.py exists"
echo "- ✅ requirements.txt exists"
echo "- Check GitHub repository connection in Vercel dashboard"
echo "- Check environment variables in Vercel project settings"
echo "- Monitor build logs in Vercel dashboard"

echo ""
echo "🔗 Useful Links:"
echo "- Vercel Dashboard: https://vercel.com/dashboard"
echo "- GitHub Actions: https://github.com/abdulrahimiqbal/pantheon/actions"
echo "- Project Repository: https://github.com/abdulrahimiqbal/pantheon" 