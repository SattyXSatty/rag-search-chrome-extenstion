# Installation Fix

## Issue
The original requirements.txt had outdated package versions that are no longer available.

## Fixed

Updated `backend/requirements.txt` to use flexible versions:
- `faiss-cpu>=1.9.0` (was 1.7.4, which doesn't exist)
- All other packages use `>=` for compatibility

## Clean Install Steps

```bash
# 1. Remove old virtual environment
rm -rf backend/venv

# 2. Run the updated start script
./start-backend.sh
```

The script will now:
1. Create fresh virtual environment
2. Upgrade pip first
3. Install all dependencies with correct versions
4. Verify installation before starting server

## Manual Installation (if script fails)

```bash
cd backend

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install flask flask-cors faiss-cpu sentence-transformers numpy torch

# Start server
python server.py
```

## Verify Installation

```bash
# Check if packages installed
pip list | grep -E "flask|faiss|sentence"

# Should show:
# faiss-cpu        1.9.0 (or higher)
# flask            3.0.0 (or higher)
# flask-cors       4.0.0 (or higher)
# sentence-transformers 2.2.2 (or higher)
```

## Common Issues

### Issue: "No module named 'flask'"
**Solution:** Virtual environment not activated
```bash
source backend/venv/bin/activate
```

### Issue: "Could not find a version that satisfies the requirement"
**Solution:** Update pip first
```bash
pip install --upgrade pip
```

### Issue: "Python not found"
**Solution:** Install Python 3.8+
```bash
# macOS
brew install python

# Ubuntu/Debian
sudo apt install python3 python3-venv

# Windows
# Download from python.org
```

## Now Try Again

```bash
./start-backend.sh
```

Should work perfectly now! ✅
