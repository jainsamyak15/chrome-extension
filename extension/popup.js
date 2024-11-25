document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    let websiteContent = '';

    // Get website content when popup opens
    chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
        try {
            // Send message to content script
            const response = await chrome.tabs.sendMessage(tabs[0].id, {
                action: "getPageContent"
            });
            websiteContent = response.content;
            console.log("Website content loaded:", websiteContent.substring(0, 100) + "..."); // Debug log
        } catch (error) {
            console.error('Error getting page content:', error);
            websiteContent = 'Error: Could not fetch page content';
        }
    });

    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';

        // Add placeholder for assistant response
        const assistantMessageDiv = addMessage('Thinking...', false);

        try {
            console.log('Sending request to server...'); // Debug log

            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    website_content: websiteContent,
                    user_message: message
                })
            });

            console.log('Response status:', response.status); // Debug log

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received response:', data); // Debug log

            if (data.error) {
                throw new Error(data.error);
            }

            // Update assistant message with response
            assistantMessageDiv.textContent = data.response;

        } catch (error) {
            console.error('Error in sendMessage:', error);
            assistantMessageDiv.textContent = `Error: ${error.message}`;
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});