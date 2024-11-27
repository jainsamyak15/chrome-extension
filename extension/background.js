// Handle installation and updates
chrome.runtime.onInstalled.addListener(() => {
    console.log('Extension installed');
});

// Initialize connection with content scripts
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && /^http/.test(tab.url)) {
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).catch(err => console.error(err));
    }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getPageContent") {
        chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
            try {
                const response = await chrome.tabs.sendMessage(tabs[0].id, { action: "getPageContent" });
                sendResponse(response);
            } catch (error) {
                sendResponse({ error: "Failed to get page content" });
            }
        });
        return true;
    }
});