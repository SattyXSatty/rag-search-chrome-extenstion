# 🧪 Test the Highlighting Fix

## Quick Test Steps

### 1. Reload the Extension
```
1. Open Chrome and go to: chrome://extensions/
2. Find "Web Memory RAG"
3. Click the reload icon (circular arrow)
4. Verify version shows: 2.0.8
```

### 2. Test with Wikipedia Example

**Search Query:** `India women's national cricket team`

**Steps:**
1. Open extension popup
2. Type: `India women's national cricket team`
3. Press Enter or click Search
4. Click on any Wikipedia result

**Expected Result:**
- ✅ Only the page title should be highlighted
- ✅ Maybe 1-2 relevant paragraphs with multiple matching words
- ✅ Should scroll to the first highlight
- ❌ NOT the entire page covered in yellow

### 3. Test with Other Queries

**Test Case 1: Single Word**
- Query: `laptop`
- Expected: Very minimal highlighting (only where "laptop" appears in context)

**Test Case 2: Technical Query**
- Query: `chrome extension development`
- Expected: Highlights sections about Chrome extensions and development

**Test Case 3: Short Common Words**
- Query: `how to use git`
- Expected: Only highlights "use" (3 chars ignored), so minimal highlighting

## What Changed?

### Before (v2.0.6-2.0.7):
```javascript
// Passed the entire matched snippet (hundreds of words)
openAndHighlight(url, snippet);

// Extracted ALL words 4+ characters
const words = snippet.match(/\b\w{4,}\b/g);
// Result: 50+ words like "india", "team", "they", "have", "been", etc.

// Highlighted 50+ nodes
nodesToHighlight.slice(0, 50).forEach(...)
```

### After (v2.0.8):
```javascript
// Pass only the original search query
openAndHighlight(url, query);

// Extract only meaningful words (5+ characters)
const words = query.match(/\b\w{5,}\b/g);
// Result: 3-5 distinctive words

// Require 2+ word matches per node
const minMatches = words.length === 1 ? 1 : 2;

// Highlight only top 20 most relevant nodes
topNodes.slice(0, 20).forEach(...)
```

## Debugging

If highlighting still seems off:

### Check Console Logs:
1. Open DevTools (F12)
2. Go to Console tab
3. Look for these messages:
   ```
   🎨 Highlighting in page: India women's national cricket team
   Looking for words: ["india", "women", "national", "cricket"]
   Using distinctive words: ["india", "women", "national", "cricket"]
   Found 15 matching nodes, highlighting top 15
   ✅ Scrolled to first highlight
   ```

### Verify Data Flow:
1. In popup, check what's being passed:
   ```
   🖱️ Result clicked! https://...
   🔍 Query: India women's national cricket team  ← Should be the search query
   📄 Snippet: India women's national cricket...  ← Not used anymore
   ```

2. In background, check what's received:
   ```
   🎯 OPEN_AND_HIGHLIGHT received!
   🔗 url: https://...
   🔍 Search query: India women's national cricket team  ← Correct!
   ```

## Success Criteria

✅ **Pass:** Highlighting is precise and relevant
✅ **Pass:** Only 5-20 highlights per page (not 50+)
✅ **Pass:** Highlights contain multiple search words
✅ **Pass:** Scrolls to first highlight automatically

❌ **Fail:** Entire page is yellow
❌ **Fail:** Random words highlighted everywhere
❌ **Fail:** No highlighting at all

## If It Still Doesn't Work

1. **Hard refresh the extension:**
   - Remove the extension completely
   - Re-add it from the folder
   - Test again

2. **Check the files were updated:**
   ```bash
   # Verify version
   grep version manifest.json
   # Should show: "version": "2.0.8"
   
   # Verify popup.js uses query not snippet
   grep "item.dataset.query" popup.js
   # Should find 2 occurrences
   
   # Verify background.js uses 5+ char words
   grep "\\b\\\\w{5,}\\\\b" background.js
   # Should find the pattern
   ```

3. **Check browser cache:**
   - Close all Chrome windows
   - Reopen Chrome
   - Test again

---

**Expected Outcome:** Clean, precise highlighting that helps you find what you searched for! 🎯
