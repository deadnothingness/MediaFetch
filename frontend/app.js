// API configuration
const API_BASE_URL = window.location.origin;

// DOM elements
const downloadForm = document.getElementById('downloadForm');
const submitBtn = document.getElementById('submitBtn');
const tasksList = document.getElementById('tasksList');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatMessages = document.getElementById('chatMessages');

// ---- Helper functions ----

function formatStatus(status) {
    const statusMap = {
        'pending': '⏳ Pending',
        'downloading': '⬇️ Downloading',
        'completed': '✅ Completed',
        'failed': '❌ Failed'
    };
    return statusMap[status] || status;
}

function getStatusClass(status) {
    const classMap = {
        'pending': 'status-pending',
        'downloading': 'status-downloading',
        'completed': 'status-completed',
        'failed': 'status-failed'
    };
    return classMap[status] || 'status-pending';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function truncateUrl(url, maxLength = 50) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
}

function addChatMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// ---- Task management ----

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

function displayTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = '<div class="loading">📭 No downloads yet. Create your first one above!</div>';
        return;
    }

    tasksList.innerHTML = tasks.map(task => `
        <div class="task-card" data-task-id="${task.id}">
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
            ${task.status === 'downloading' ? `
                <div class="progress-container">
                    <div class="progress-bar" style="width: ${task.progress || 0}%"></div>
                    <div class="progress-text">${task.progress || 0}%</div>
                </div>
            ` : ''}
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
    
    // Subscribe to progress for downloading tasks
    tasks.forEach(task => {
        if (task.status === 'downloading') {
            const taskCard = document.querySelector(`.task-card[data-task-id="${task.id}"]`);
            if (taskCard) {
                subscribeToProgress(task.id, taskCard);
            }
        }
    });
}

// ---- Download logic ----

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

    submitBtn.disabled = true;
    submitBtn.textContent = 'Starting download...';

    try {
        await startDownload(url, format, quality);
        urlInput.value = '';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Start Download';
    }
}

// ---- Chat / LLM logic ----

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

    if (parsed.search_query && !parsed.url) {
        urlInput.value = parsed.search_query;
    }
}

async function handleChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    chatInput.value = '';
    chatSendBtn.disabled = true;

    addChatMessage(message, true);
    showTypingIndicator();

    try {
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

// ---- Auto-refresh ----

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

// ---- App initialization ----

document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();
    startAutoRefresh();

    downloadForm.addEventListener('submit', handleSubmit);

    chatSendBtn.addEventListener('click', handleChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleChatMessage();
        }
    });

    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });
});

function subscribeToProgress(taskId, taskCard) {
    const eventSource = new EventSource(`${API_BASE_URL}/tasks/${taskId}/progress`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const progressBar = taskCard.querySelector('.progress-bar');
        const progressText = taskCard.querySelector('.progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.setAttribute('aria-valuenow', data.progress);
        }
        if (progressText) {
            progressText.textContent = `${data.progress}%`;
        }
        
        if (data.status === 'completed') {
            eventSource.close();
            // Refresh tasks to show download button
            fetchTasks();
        } else if (data.status === 'failed') {
            eventSource.close();
            // Show error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = `⚠️ Error: ${data.error || 'Download failed'}`;
            taskCard.appendChild(errorDiv);
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
    };
}