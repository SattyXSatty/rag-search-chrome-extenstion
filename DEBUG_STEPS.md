# Debug Steps - Find Where It's Breaking

## Step 1: Reload Extension
```
chrome://extensions/ → Reload "Web Memory RAG"
```

## Step 2: Open Service Worker Console
```
1. chrome://extensions/
2. Find "Web Memory RAG"
3. Click "service worker" link
4. Console opens
5. Keep this open!
```

## Step 3: Test Search
```
1. Click extension icon
2. Type: "machine learning"
3. Watch service worker console
```

### What You Should See:
```
📨 Background received message: SEARCH_CONTENT
🔍 Search request: machine learning category: all
```

### If You DON'T See This:
- Search isn't working
- Check popup console (right-click popup → Inspect)

## Step 4: Click Result
```
1. Click any search result
2. Watch service worker console
```

### What You Should See:
```
📨 Background received message: SCHEDULE_HIGHLIGHT
🎯 SCHEDULE_HIGHLIGHT received! tabId: 123 text: machine learning
📅 Scheduled highlight for tab: 123 query: machine learning
📊 Tab status: complete (or loading)
```

### If You DON'T See This:
- Message not being sent from popup
- Check popup console for errors

## Step 5: Watch for Highlight Execution
```
Keep watching service worker console
```

### What You Should See:
```
✅ Tab already loaded, executing highlight now
🎯 Executing highlight for tab: 123
✅ Highlight script executed successfully
```

OR

```
⏳ Waiting for tab to load...
📊 Tab 123 update: loading
📊 Tab 123 update: complete
✅ Page loaded completely
🎯 Executing highlight for tab: 123
✅ Highlight script executed successfully
```

## Step 6: Check Page Console
```
1. Go to the opened tab
2. Press F12
3. Check console
```

### What You Should See:
```
🎨 Highlighting in page: machine learning
Looking for words: ["machine", "learning"]
Found nodes to highlight: X
✅ Scrolled to first highlight
```

## Troubleshooting

### No "SEARCH_CONTENT" Message
**Problem:** Search not working
**Check:** 
- Is backend running? `curl http://localhost:8000/health`
- Check popup console for errors

### No "SCHEDULE_HIGHLIGHT" Message
**Problem:** Click handler not working
**Check:**
- Are there search results displayed?
- Check popup console when clicking

### "SCHEDULE_HIGHLIGHT" Received But No Execution
**Problem:** Tab status check or listener issue
**Check:**
- What does "Tab status:" show?
- Does it say "Waiting for tab to load..."?
- Do you see "Tab X update:" messages?

### "Highlight script executed" But No Highlights
**Problem:** Script injection worked but highlighting failed
**Check:**
- Page console for errors
- Is the page blocking scripts?
- Try on a simple page like TEST_HIGHLIGHTING.html

## Expected Full Flow

```
Service Worker Console:
📨 Background received message: SEARCH_CONTENT
🔍 Search request: machine learning category: all
📨 Background received message: SCHEDULE_HIGHLIGHT
🎯 SCHEDULE_HIGHLIGHT received! tabId: 123 text: machine learning
📅 Scheduled highlight for tab: 123 query: machine learning
📊 Tab status: complete URL: https://...
✅ Tab already loaded, executing highlight now
🎯 Executing highlight for tab: 123
✅ Highlight script executed successfully

Page Console:
🎨 Highlighting in page: machine learning
Looking for words: ["machine", "learning"]
Found nodes to highlight: 12
✅ Scrolled to first highlight
```

## Quick Test

Try this in service worker console:
```javascript
// Test if highlighting function works
chrome.tabs.query({active: true}, (tabs) => {
  chrome.scripting.executeScript({
    target: { tabId: tabs[0].id },
    func: (text) => {
      alert('Highlighting: ' + text);
    },
    args: ['test']
  });
});
```

Should show an alert on the active tab.

---

**Follow these steps and tell me where it breaks!**
**Share the console output at each step.**
