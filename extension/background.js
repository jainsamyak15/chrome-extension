chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getPageContent") {
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      function: () => document.body.innerText
    }, (result) => {
      sendResponse({ content: result[0].result });
    });
    return true;
  }
});