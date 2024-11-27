document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const statusIndicator = document.getElementById('status-indicator');

    let websiteContent = '';
    let isProcessing = false;
    let currentUrl = '';

    function updateConnectionStatus(isOnline) {
        statusIndicator.className = isOnline ? 'online' : 'offline';
        statusIndicator.innerHTML = `<i class="fas fa-circle"></i> ${isOnline ? 'Connected' : 'Offline'}`;
    }

    async function getCurrentTab() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        return tab;
    }

    async function checkServerConnection() {
        try {
            const response = await fetch('http://localhost:3000/api/chat', {
                method: 'OPTIONS',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            updateConnectionStatus(response.ok);
            return response.ok;
        } catch (error) {
            console.error('Server connection error:', error);
            updateConnectionStatus(false);
            return false;
        }
    }

    async function getPageContent() {
        try {
            const tab = await getCurrentTab();
            if (!tab?.id) {
                console.error('No active tab found');
                return 'No active tab found';
            }
            currentUrl = tab.url;
            console.log('Current URL:', currentUrl);

            return new Promise((resolve) => {
                chrome.tabs.sendMessage(tab.id, { action: "getPageContent" }, (response) => {
                    if (chrome.runtime.lastError) {
                        console.error('Runtime error:', chrome.runtime.lastError);
                        setTimeout(() => {
                            getPageContent().then(resolve);
                        }, 100);
                        return;
                    }
                    console.log('Content received:', response?.content?.substring(0, 200) + '...');
                    resolve(response?.content || 'No content available');
                });
            });
        } catch (error) {
            console.error('Error getting page content:', error);
            return 'Error getting page content';
        }
    }

    async function initializeChat() {
        try {
            websiteContent = await getPageContent();
            console.log('Initialized with content length:', websiteContent.length);
            const isConnected = await checkServerConnection();
            updateConnectionStatus(isConnected);

            addMessage('Hello! I\'m ready to help you understand this webpage. What would you like to know?', false);
        } catch (error) {
            console.error('Error initializing chat:', error);
            updateConnectionStatus(false);
        }
    }

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

        if (!isUser && content === 'thinking') {
            messageDiv.innerHTML = '<div class="typing-indicator"><span>.</span><span>.</span><span>.</span></div>';
        } else {
            messageDiv.textContent = content;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    async function sendMessage() {
        if (isProcessing) return;

        const message = userInput.value.trim();
        if (!message) return;

        isProcessing = true;
        sendButton.disabled = true;

        addMessage(message, true);
        userInput.value = '';

        const assistantMessageDiv = addMessage('thinking', false);
        try {
            console.log('Sending request with content length:', websiteContent.length);
            const response = await fetch('http://localhost:3000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    website_content: websiteContent,
                    user_message: message,
                    url: currentUrl
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            console.log('Response received:', data);

            if (data.error) {
                throw new Error(data.error);
            }

            assistantMessageDiv.textContent = data.response;
            updateConnectionStatus(true);

        } catch (error) {
            console.error('Error:', error);
            assistantMessageDiv.textContent = 'Sorry, I encountered an error. Please try again later.';
            updateConnectionStatus(false);
        } finally {
            isProcessing = false;
            sendButton.disabled = false;
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Initialize when popup opens
    initializeChat();
    userInput.focus();
});