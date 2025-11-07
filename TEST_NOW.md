# Test the Highlighting Now

## Step 1: Clean Start

### 1.1 Reload Extension
```
1. Go to: chrome://extensions/
2. Find: "Web Memory RAG"
3. Click: Reload button (🔄)
```

### 1.2 Close All Tabs
```
Close all tabs except this one
```

### 1.3 Refresh This Page
```
Press F5 or Ctrl+R to refresh
(This loads the new content script)
```

## Step 2: Test Highlighting

### 2.1 Open Test Page
```
1. Open: TEST_HIGHLIGHTING.html in Chrome
2. Wait: 3 seconds
3. Check backend console: Should see "Captured: ..."
```

### 2.2 Search
```
1. Click: Extension icon
2. Type: "machine learning"
3. Wait: For results
4. Click: The TEST_HIGHLIGHTING.html result
```

### 2.3 What Should Happen
```
✅ New tab opens (or existing tab activates)
✅ Wait 2-3 seconds
✅ Yellow highlights appear on "machine" and "learning"
✅ Page scrolls to first highlight
```

## Step 3: Check Consoles

### 3.1 Background Console
```
1. chrome://extensions/
2. Click: "service worker" link
3. Should see:
   - "Scheduled highlight for tab: X"
   - "Page loaded completely"
   - "Highlight script executed"
```

### 3.2 Page Console
```
1. On the highlighted page
2. Press: F12
3. Go to: Console tab
4. Should see:
   - "Highlighting in page: machine learning"
   - "Looking for words: ['machine', 'learning']"
   - "Found nodes to highlight: X"
   - "Scrolled to first highlight"
```

## Step 4: If It Doesn't Work

### Check 1: Is Backend Running?
```bash
curl http://localhost:8000/health
```

Should return: `{"status": "healthy", ...}`

### Check 2: Was Page Captured?
```
Look in background console for:
"Captured: [URL]"
```

### Check 3: Did Search Return Results?
```
In popup, after searching, should see results listed
```

### Check 4: Check for Errors
```
Background console: Any red errors?
Page console: Any red errors?
```

## Common Issues

### Issue: "Extension context invalidated"
**Solution:** This is from old pages. Just refresh the page (F5).

### Issue: No highlights appear
**Check:**
1. Did you reload the extension?
2. Did you refresh the page?
3. Is the search query correct?
4. Check background console for "Highlight script executed"

### Issue: Wrong words highlighted
**Check:** Are you searching for the right terms?
The extension highlights words from your search query.

## Quick Debug

### Test Direct Injection
```javascript
// In background console (chrome://extensions/ → service worker):
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  chrome.scripting.executeScript({
    target: { tabId: tabs[0].id },
    func: () => {
      alert('Script injection works!');
    }
  });
});
```

Should show an alert on the active tab.

### Test Highlighting Function
```javascript
// In background console:
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  chrome.scripting.executeScript({
    target: { tabId: tabs[0].id },
    func: (query) => {
      // Paste the highlightTextInPage function here
      console.log('Testing highlight with:', query);
    },
    args: ['test words']
  });
});
```

## Expected Timeline

```
0s    - Click result
0.1s  - New tab created
0.2s  - Background receives SCHEDULE_HIGHLIGHT
1-3s  - Page loads
3-4s  - Background waits 1 second
4s    - Background injects highlighting script
4.1s  - Highlights appear ✅
4.2s  - Page scrolls ✅
```

## Success Criteria

✅ Extension reloaded
✅ Pages refreshed
✅ Search returns results
✅ Click opens page
✅ Highlights appear (yellow background)
✅ Page scrolls to first match
✅ Console shows success messages
✅ No red errors

---

**If all checks pass, highlighting is working!**
**If not, share the console output and I'll help debug.**
