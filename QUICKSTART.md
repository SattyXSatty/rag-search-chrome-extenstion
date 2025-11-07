# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Start Backend (Terminal)

### macOS/Linux:
```bash
./start-backend.sh
```

### Windows:
```bash
start-backend.bat
```

**First time?** It will:
- Create virtual environment
- Install dependencies (~2-3 minutes)
- Download Nomic model (~1GB, one-time)
- Start server on http://localhost:8000

**Already setup?** Starts instantly!

## Step 2: Install Extension (Chrome)

1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select this folder
5. Done! 🎉

## Step 3: Test It

1. **Browse some websites**:
   - Visit 5-10 different sites
   - Wait 2-3 seconds per page
   - Check backend terminal for "Captured: ..." messages

2. **Search your history**:
   - Click extension icon
   - Type anything you remember from those pages
   - See semantic search results!

3. **Try product comparison**:
   - Visit Amazon, eBay, or any shopping site
   - Search for products
   - Click "🛒 Shopping" filter in extension
   - Search for product name
   - See comparison across all sites!

## Verify Setup

### Check Backend:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "model": "nomic-ai/nomic-embed-text-v1.5",
  "total_vectors": 0,
  "dimension": 768
}
```

### Check Extension:
- Click extension icon
- Should show: "🟢 FAISS Backend Connected"
- If shows "🟡 Using Local Storage", backend isn't running

## Troubleshooting

### Backend won't start?

**Python not found:**
```bash
# Install Python 3.8+
# macOS: brew install python
# Windows: Download from python.org
```

**Dependencies fail:**
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Extension not capturing?

1. Check browser console (F12) for errors
2. Verify you're not on excluded sites (Gmail, etc.)
3. Refresh page after installing extension

### Search returns nothing?

1. Browse more pages first (need data!)
2. Check backend logs for "Captured: ..." messages
3. Try simpler search terms

## What's Next?

- **Let it run**: Browse normally for a day
- **Build your index**: Visit 100+ pages
- **Try categories**: Filter by News, Docs, Social, Video
- **Compare products**: Shop around, then compare in extension
- **Customize**: Edit `background.js` to add your own categories

## Need Help?

Check the full guides:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [README.md](README.md) - Full documentation
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Advanced features

Enjoy your personal web memory! 🧠✨
