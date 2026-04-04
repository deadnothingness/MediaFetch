// API configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
const downloadForm = document.getElementById('downloadForm');
const submitBtn = document.getElementById('submitBtn');
const tasksList = document.getElementById('tasksList');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

// Helper function to format status text
function formatStatus(status) {
    const statusMap = {
        'pending': '⏳ Pending',
        'downloading': '⬇️ Downloading',
        'completed': '✅ Completed',
        'failed': '❌ Failed'
    };
    return statusMap[status] || status;
}

// Helper function to get status CSS class
function getStatusClass(status) {
    const classMap = {
        'pending': 'status-pending',
        'downloading': 'status-downloading',
        'completed': 'status-completed',
        'failed': 'status-failed'
    };
    return classMap[status] || 'status-pending';
}

// Helper function to format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Helper function to truncate long URLs
function truncateUrl(url, maxLength = 50) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
}

// Fetch and display all tasks
async function fetchTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const tasks = await response.json();
        displayTasks(tasks);
    } catch (error) {
        console.error('Error fetching tasks:', error);
        tasksList.innerHTML = '<div class="loading">❌ Failed to load tasks. Make sure the backend is running.</div>';
    }
}

// Display tasks in the UI
function displayTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = '<div class="loading">📭 No downloads yet. Create your first one above!</div>';
        return;
    }

    tasksList.innerHTML = tasks.map(task => `
        <div class="task-card">
            <div class="task-header">
                <span class="task-status ${getStatusClass(task.status)}">
                    ${formatStatus(task.status)}
                </span>
            </div>
            <div class="task-url">
                🔗 ${truncateUrl(task.url)}
            </div>
            <div class="task-details">
                📁 ${task.format.toUpperCase()} • 🎚️ ${task.quality} quality
                ${task.created_at ? ` • 🕐 ${formatDate(task.created_at)}` : ''}
            </div>
            ${task.status === 'completed' && task.id ? `
                <a href="${API_BASE_URL}/download/${task.id}" class="download-link" download>
                    ⬇️ Download File
                </a>
            ` : ''}
            ${task.status === 'failed' && task.error_message ? `
                <div class="error-message">
                    ⚠️ Error: ${task.error_message.substring(0, 100)}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Start a new download
async function startDownload(url, format, quality) {
    try {
        const response = await fetch(`${API_BASE_URL}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                format: format,
                quality: quality
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const result = await response.json();
        console.log('Download started:', result);
        
        // Refresh tasks list immediately
        await fetchTasks();
        
        return result;
    } catch (error) {
        console.error('Error starting download:', error);
        alert(`Failed to start download: ${error.message}`);
        throw error;
    }
}

// Handle form submission
async function handleSubmit(event) {
    event.preventDefault();
    
    const urlInput = document.getElementById('url');
    const formatSelect = document.getElementById('format');
    const qualitySelect = document.getElementById('quality');
    
    const url = urlInput.value.trim();
    const format = formatSelect.value;
    const quality = qualitySelect.value;
    
    if (!url) {
        alert('Please enter a URL or search query');
        return;
    }
    
    // Disable button while processing
    submitBtn.disabled = true;
    submitBtn.textContent = 'Starting download...';
    
    try {
        await startDownload(url, format, quality);
        urlInput.value = ''; // Clear the input field on success
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Start Download';
    }
}

// Auto-refresh tasks every 3 seconds
let refreshInterval = null;

function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    refreshInterval = setInterval(fetchTasks, 3000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Initialize the app
function init() {
    // Load tasks on page load
    fetchTasks();
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Attach form submit handler
    downloadForm.addEventListener('submit', handleSubmit);
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Add message to chat
function addChatMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Parse natural language with LLM
async function parseWithLLM(message) {
    try {
        const response = await fetch(`${API_BASE_URL}/llm/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('LLM parse error:', error);
        return null;
    }
}

// Fill manual form with parsed data
function fillFormWithParsedData(parsed) {
    const urlInput = document.getElementById('url');
    const formatSelect = document.getElementById('format');
    const qualitySelect = document.getElementById('quality');
    
    if (parsed.url) {
        urlInput.value = parsed.url;
    }
    
    if (parsed.format && (parsed.format === 'mp3' || parsed.format === 'mp4')) {
        formatSelect.value = parsed.format;
    }
    
    if (parsed.quality && ['low', 'medium', 'high'].includes(parsed.quality)) {
        qualitySelect.value = parsed.quality;
    }
    
    // If search_query and no URL, put search query in URL field (will be handled by backend later)
    if (parsed.search_query && !parsed.url) {
        urlInput.value = parsed.search_query;
    }
}

// Handle chat message submission
async function handleChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Clear input and disable button
    chatInput.value = '';
    chatSendBtn.disabled = true;
    
    // Add user message to chat
    addChatMessage(message, true);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send to LLM for parsing
        const parsed = await parseWithLLM(message);
        
        removeTypingIndicator();
        
        if (parsed) {
            let responseMessage = '';
            
            if (parsed.url) {
                responseMessage = `I found a URL: ${parsed.url.substring(0, 50)}...\n`;
                if (parsed.format) {
                    responseMessage += `Format: ${parsed.format.toUpperCase()}\n`;
                }
                if (parsed.quality) {
                    responseMessage += `Quality: ${parsed.quality}\n`;
                }
                responseMessage += `\nI've filled the form below. Click "Start Download" to begin!`;
                
                // Fill the form
                fillFormWithParsedData(parsed);
            } else if (parsed.search_query) {
                responseMessage = `I'll search for "${parsed.search_query}".\n`;
                if (parsed.format) {
                    responseMessage += `Format: ${parsed.format.toUpperCase()}\n`;
                }
                responseMessage += `\nEntered search term in the URL field. Click "Start Download" to search and download.`;
                
                fillFormWithParsedData(parsed);
            } else {
                responseMessage = `I couldn't understand what you want to download. Please try:\n\n"Download this video: [URL]"\n"Save audio from [URL] in high quality"`;
            }
            
            addChatMessage(responseMessage);
        } else {
            addChatMessage("Sorry, I'm having trouble understanding. Please try again or use the manual form.");
        }
    } catch (error) {
        removeTypingIndicator();
        console.error('Chat error:', error);
        addChatMessage("Sorry, something went wrong. Please try again later.");
    } finally {
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}

// Add event listeners for chat (add to init() function)
// Also add Enter key support
function initChat() {
    chatSendBtn.addEventListener('click', handleChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleChatMessage();
        }
    });
}

// Update the existing init() function to include chat initialization
// Replace the existing init() function with this:

function init() {
    // Load tasks on page load
    fetchTasks();
    
    // Start auto-refresh
    startAutoRefresh();
    
    // Attach form submit handler
    downloadForm.addEventListener('submit', handleSubmit);
    
    // Initialize chat
    initChat();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });
}