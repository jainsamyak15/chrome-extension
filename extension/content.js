// Initialize message passing
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getPageContent") {
        const content = getPageContent();
        console.log('Scraped content:', content); // Log the content
        sendResponse({ content });
    }
    return true;
});

function getPageContent() {
    // Get all visible text content
    const content = Array.from(document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, article, section, div'))
        .map(element => element.innerText)
        .filter(text => text.trim().length > 0)
        .join('\n');

    console.log('Raw scraped content:', content); // Log raw content
    return content;
}