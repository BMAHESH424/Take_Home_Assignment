// Local state only - the API is stateless as per requirements
let conversationHistory = [];

async function sendMessage() {
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const text = input.value.trim();
    
    if (!text) return;

    // 1. Update UI with User Message
    appendMessage(text, 'user');
    
    // 2. Prepare the stateless payload
    conversationHistory.push({ role: "user", content: text });
    input.value = '';
    
    // Disable input while waiting for the "agent brain" to process
    input.disabled = true;
    sendBtn.disabled = true;

    try {
        // 3. Connect to the FastAPI backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversationHistory })
        });

        if (!response.ok) throw new Error("Server communication failed");

        const data = await response.json();

        // 4. Update UI with Bot Reply and Grounded Recommendations
        appendMessage(data.reply, 'bot', data.recommendations);
        
        // 5. Update history for the next turn to maintain context
        conversationHistory.push({ role: "assistant", content: data.reply });
        
        // Handle end of conversation flag
        if (data.end_of_conversation) {
            input.placeholder = "Conversation ended.";
        } else {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
        
    } catch (error) {
        console.error("Connection failed:", error);
        appendMessage("I'm sorry, I encountered an error connecting to the catalog. Please try again.", 'bot');
        input.disabled = false;
        sendBtn.disabled = false;
    }
}

/**
 * Renders messages and structured recommendation cards
 * @param {string} text - The agent's conversational reply
 * @param {string} role - 'user' or 'bot'
 * @param {Array} recs - Grounded shortlist from the catalog metadata
 */
function appendMessage(text, role, recs = []) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    
    // Use the standard 'msg' class for styling, adding role for alignment
    msgDiv.className = `msg ${role}`;
    
    // Create text container for the reply
    const textElement = document.createElement('p');
    textElement.innerText = text;
    msgDiv.appendChild(textElement);

    // Render structured recommendation cards if present
    if (recs && recs.length > 0) {
        const container = document.createElement('div');
        container.className = 'recommendations-container';
        
        recs.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'rec-card';
            
            // test_type mapping for human-readable labels
            const typeLabel = rec.test_type === 'P' ? 'PERSONALITY' : 'KNOWLEDGE/SKILL';
            
            // Use absolute URL and target="_blank" to ensure external navigation
            card.innerHTML = `
                <small class="rec-type">${typeLabel}</small>
                <h4>${rec.name}</h4>
                <a href="${rec.url}" target="_blank" rel="noopener noreferrer" class="view-link">View in Catalog →</a>
            `;
            container.appendChild(card);
        });
        msgDiv.appendChild(container);
    }

    chatBox.appendChild(msgDiv);
    
    // Smooth scroll to the latest message
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

// Allow pressing 'Enter' to send messages
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});