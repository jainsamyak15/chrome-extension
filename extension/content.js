function getPageContent() {
    return document.body.innerText;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getPageContent") {
        sendResponse({ content: getPageContent() });
    }
    return true;  // Will respond asynchronously
});