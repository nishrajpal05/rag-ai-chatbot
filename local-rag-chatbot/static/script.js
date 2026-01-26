// API Base URL
const API_BASE = '/api';

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadStatus = document.getElementById('uploadStatus');
const urlInput = document.getElementById('urlInput');
const scrapeBtn = document.getElementById('scrapeBtn');
const scrapeStatus = document.getElementById('scrapeStatus');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const clearBtn = document.getElementById('clearBtn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const docCount = document.getElementById('docCount');
const chunkCount = document.getElementById('chunkCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // File upload
    fileInput.addEventListener('change', handleFileUpload);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileUpload();
        }
    });
    
    // Scrape button
    scrapeBtn.addEventListener('click', handleScrape);
    
    // Send button
    sendBtn.addEventListener('click', handleQuestion);
    
    // Enter key in question input
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuestion();
        }
    });
    
    // Auto-resize textarea
    questionInput.addEventListener('input', () => {
        questionInput.style.height = 'auto';
        questionInput.style.height = questionInput.scrollHeight + 'px';
    });
    
    // Clear button
    clearBtn.addEventListener('click', handleClear);
}

// Check System Status
async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.vector_store_ready) {
            statusIndicator.classList.add('ready');
            statusText.textContent = 'Ready';
            sendBtn.disabled = false;
        } else {
            statusText.textContent = 'No documents loaded';
            sendBtn.disabled = true;
        }
        
        docCount.textContent = data.documents_loaded || 0;
        chunkCount.textContent = data.documents_loaded || 0;
        
    } catch (error) {
        console.error('Status check failed:', error);
        statusText.textContent = 'System error';
    }
}

// Handle File Upload
async function handleFileUpload() {
    const file = fileInput.files[0];
    if (!file) return;
    
    showStatus(uploadStatus, 'Uploading and processing...', 'loading');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(uploadStatus, `✓ ${data.message} (${data.chunks_created} chunks)`, 'success');
            checkStatus();
            fileInput.value = '';
        } else {
            showStatus(uploadStatus, `✗ ${data.message}`, 'error');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus(uploadStatus, '✗ Upload failed', 'error');
    }
}

// Handle Web Scraping
async function handleScrape() {
    const url = urlInput.value.trim();
    if (!url) {
        showStatus(scrapeStatus, 'Please enter a URL', 'error');
        return;
    }
    
    showStatus(scrapeStatus, 'Scraping website...', 'loading');
    scrapeBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus(scrapeStatus, `✓ ${data.message} (${data.chunks_created} chunks)`, 'success');
            checkStatus();
            urlInput.value = '';
        } else {
            showStatus(scrapeStatus, `✗ ${data.message}`, 'error');
        }
        
    } catch (error) {
        console.error('Scrape error:', error);
        showStatus(scrapeStatus, '✗ Scraping failed', 'error');
    } finally {
        scrapeBtn.disabled = false;
    }
}

// Handle Question
async function handleQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;
    
    // Add user message
    addMessage('user', question);
    questionInput.value = '';
    questionInput.style.height = 'auto';
    
    // Show loading
    const loadingId = addMessage('assistant', 'Thinking...', null, null, true);
    
    try {
        const response = await fetch(`${API_BASE}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Remove loading message
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();
        
        // Add assistant response
        addMessage('assistant', data.answer, data.sources, data.confidence);
        
    } catch (error) {
        console.error('Question error:', error);
        const loadingMsg = document.getElementById(loadingId);
        if (loadingMsg) loadingMsg.remove();
        addMessage('assistant', 'Sorry, an error occurred while processing your question.');
    }
}

// Add Message to Chat
function addMessage(role, content, sources = null, confidence = null, isLoading = false) {
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.id = messageId;
    
    let html = `
        <div class="message-header">${role === 'user' ? 'You' : 'Assistant'}</div>
        <div class="message-content">
            ${content}
    `;
    
    if (sources && sources.length > 0) {
        html += `
            <div class="message-sources">
                <strong> Sources:</strong>
                <ul>
                    ${sources.map(s => `<li>• ${s}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (confidence) {
        html += `<span class="confidence-badge confidence-${confidence}">Confidence: ${confidence}</span>`;
    }
    
    html += `</div>`;
    messageDiv.innerHTML = html;
    
    // Remove welcome message if exists
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Handle Clear
async function handleClear() {
    if (!confirm('Clear all documents? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE}/clear`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <h2>👋 Welcome!</h2>
                    <p>Upload a document or scrape a website to get started.</p>
                    <p>Then ask me anything about the content.</p>
                </div>
            `;
            checkStatus();
            showStatus(uploadStatus, '✓ All documents cleared', 'success');
        }
    } catch (error) {
        console.error('Clear error:', error);
        showStatus(uploadStatus, '✗ Clear failed', 'error');
    }
}

// Show Status Message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type} show`;
    
    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}