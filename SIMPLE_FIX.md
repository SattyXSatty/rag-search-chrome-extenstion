# Simple Fix - Let's Start Over with a Working Approach

## Current Issues

1. "Extension context invalidated" errors (from old content scripts)
2. Highlighting not working on new tabs
3. Too many moving parts causing confusion

## The Simplest Solution

Let's use a proven approach that works in Chrome extensions:

### For New Tabs:
1. Create tab
2. Wait for it to load (using chrome.tabs.onUpdated)
3. **Inject the content script manually** (ensures it's loaded)
4. Send highlight message
5. Done!

## Let me implement this simple approach...

This will be much more reliable than trying to detect if content script is ready.
