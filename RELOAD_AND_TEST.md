# 🔄 Reload Extension & Test Highlighting

## Step 1: Reload Extension (IMPORTANT!)

The highlighting code has been updated. You MUST reload the extension:

```
1. Go to: chrome://extensions/
2. Find: "Web Memory RAG"
3. Click: The circular reload icon (🔄)
4. Done!
```

## Step 2: Test with Test Page

### Option A: Use Test Page (Easiest)

1. **Open test page:**
   ```
   File → Open File → Select TEST_HIGHLIGHTING.html
   ```

2. **Wait 2-3 seconds** (for capture)

3. **Open extension** (click icon)

4. **Search:** `machine learning`

5. **Click the result**

6. **Expected:** Yellow highlights on "machine" and "learning"

### Option B: Test with Real Website

1. **Visit:** https://en.wikipedia.org/wiki/Machine_learning

2. **Wait 2-3 seconds** (for capture)

3. **Open extension**

4. **Search:** `machine learning`

5. **Click the result**

6. **Expected:** Yellow highlights throughout the page

## Step 3: Check Console (If Not Working)

1. **Right-click page** → Inspect

2. **Go to Console tab**

3. **Look for messages:**
   - "Highlighting text: ..."
   - "Looking for words: ..."
   - "Found nodes to highlight: X"
   - "Scrolled to first highlight"

## What You Should See

### ✅ Success Looks Like:
- Yellow highlighted words
- Page scrolls to first match
- Multiple highlights visible
- Console shows "Found nodes to highlight: 5" (or more)

### ❌ Problem Looks Like:
- No highlights
- Console shows "Found nodes to highlight: 0"
- Error messages in console

## Quick Troubleshooting

### If No Highlights:

**1. Did you reload the extension?**
   - Go to chrome://extensions/
   - Click reload icon

**2. Is content script loaded?**
   - Open page console
   - Type: `typeof highlightText`
   - Should show: "function"

**3. Are there console errors?**
   - Check for red errors
   - Look for permission issues

**4. Try the test page first**
   - Open TEST_HIGHLIGHTING.html
   - It's guaranteed to work

## Test Multiple Scenarios

### Test 1: Existing Tab
1. Open Wikipedia article
2. Search in extension
3. Click result (tab already open)
4. Should highlight immediately

### Test 2: New Tab
1. Search in extension
2. Click result (new tab opens)
3. Wait for page load
4. Should highlight after load

### Test 3: Different Search Terms
- "machine learning" → highlights both words
- "neural networks" → highlights both words
- "javascript" → highlights that word
- "web development" → highlights both words

## Debug Commands

### Check if content script loaded:
```javascript
// In page console:
typeof highlightText
// Should return: "function"
```

### Manually trigger highlight:
```javascript
// In page console:
chrome.runtime.sendMessage({
  type: 'HIGHLIGHT_TEXT',
  text: 'test words to highlight'
});
```

### Check for existing highlights:
```javascript
// In page console:
document.querySelectorAll('.web-memory-highlight').length
// Should return: number of highlights
```

## Expected Console Output

When highlighting works, you'll see:
```
Highlighting text: machine learning neural networks...
Looking for words: ["machine", "learning", "neural", "networks"]
Found nodes to highlight: 12
Scrolled to first highlight
```

## Still Not Working?

### Try These:

1. **Completely remove and reinstall extension**
   ```
   1. chrome://extensions/
   2. Remove "Web Memory RAG"
   3. Load unpacked again
   ```

2. **Check site permissions**
   ```
   1. chrome://extensions/
   2. Click "Details" on extension
   3. Ensure "On all sites" is enabled
   ```

3. **Test on simple site first**
   - Use TEST_HIGHLIGHTING.html
   - Or try: https://example.com

4. **Check backend is running**
   ```bash
   curl http://localhost:8000/health
   ```

## Success Criteria

✅ Extension reloaded
✅ Test page opens
✅ Content captured (check backend logs)
✅ Search returns results
✅ Click opens page
✅ Yellow highlights appear
✅ Page scrolls to match
✅ Console shows debug info

---

**Next:** After confirming highlights work, try on real websites!

**Note:** Some sites (Gmail, banking, etc.) are excluded and won't be captured or highlighted.
