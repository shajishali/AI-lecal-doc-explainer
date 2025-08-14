// Configuration
const API_BASE_URL = process.env.DJANGO_API_URL || 'http://localhost:8000';

// Utility Functions
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ffc107';
            notification.style.color = '#333';
            break;
        default:
            notification.style.backgroundColor = '#17a2b8';
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// File Upload Handling
function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#764ba2';
        uploadArea.style.background = '#f0f2ff';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#f8f9ff';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#f8f9ff';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Click to upload functionality
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    // Validate file type
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showNotification('Please select a valid file type (PDF, DOC, DOCX, or TXT)', 'error');
        return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('File size must be less than 10MB', 'error');
        return;
    }

    // Show upload progress
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Starting upload...';

    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('document', file);
        formData.append('title', file.name);

        // Simulate upload progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
            progressText.textContent = `Uploading... ${Math.round(progress)}%`;
        }, 200);

        // Upload file to Django API
        const response = await fetch(`${API_BASE_URL}/api/documents/`, {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData, let browser set it
            }
        });

        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Processing document...';

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        // Show success message
        showNotification('Document uploaded successfully!', 'success');
        
        // Process the document
        await processDocument(result.id);
        
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Upload failed. Please try again.', 'error');
        progressText.textContent = 'Upload failed';
    } finally {
        // Hide progress after a delay
        setTimeout(() => {
            uploadProgress.style.display = 'none';
        }, 2000);
    }
}

async function processDocument(documentId) {
    try {
        // Process the document
        const processResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}/process/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!processResponse.ok) {
            throw new Error(`Processing failed: ${processResponse.status}`);
        }

        // Get document summary
        const summaryResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}/summary/`);
        const summary = await summaryResponse.json();

        // Get risk analysis
        const riskResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}/risk-analysis/`);
        const risk = await riskResponse.json();

        // Get clauses
        const clausesResponse = await fetch(`${API_BASE_URL}/api/documents/${documentId}/clauses/`);
        const clauses = await clausesResponse.json();

        // Display results
        displayResults(summary, risk, clauses);

    } catch (error) {
        console.error('Processing error:', error);
        showNotification('Document processing failed. Please try again.', 'error');
    }
}

function displayResults(summary, risk, clauses) {
    // Show results section
    const resultsSection = document.getElementById('results');
    resultsSection.style.display = 'block';

    // Display summary
    const summaryContent = document.getElementById('summaryContent');
    summaryContent.innerHTML = `
        <p><strong>Document Type:</strong> ${summary.document_type || 'Legal Document'}</p>
        <p><strong>Summary:</strong> ${summary.summary || 'Processing...'}</p>
        <p><strong>Language:</strong> ${summary.language || 'English'}</p>
    `;

    // Display risk analysis
    const riskContent = document.getElementById('riskContent');
    riskContent.innerHTML = `
        <p><strong>Risk Level:</strong> <span class="risk-level ${risk.risk_level?.toLowerCase() || 'medium'}">${risk.risk_level || 'Medium'}</span></p>
        <p><strong>Key Risks:</strong></p>
        <ul>
            ${(risk.key_risks || []).map(risk => `<li>${risk}</li>`).join('')}
        </ul>
    `;

    // Display clauses
    const clausesContent = document.getElementById('clausesContent');
    clausesContent.innerHTML = `
        <p><strong>Total Clauses:</strong> ${clauses.length || 0}</p>
        <div class="clauses-list">
            ${(clauses || []).map(clause => `
                <div class="clause-item">
                    <h4>${clause.title || 'Untitled Clause'}</h4>
                    <p>${clause.content || 'No content available'}</p>
                    <span class="clause-type">${clause.type || 'General'}</span>
                </div>
            `).join('')}
        </div>
    `;

    // Scroll to results
    scrollToSection('results');
}

// API Helper Functions
async function makeApiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

// Chat functionality
async function askQuestion(question, documentId = null) {
    try {
        const response = await makeApiCall('/api/chat/ask/', {
            method: 'POST',
            body: JSON.stringify({
                question: question,
                document_id: documentId
            })
        });
        return response;
    } catch (error) {
        showNotification('Failed to get answer. Please try again.', 'error');
        throw error;
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Legal Document Explainer initialized');
    
    // Initialize file upload functionality
    initializeFileUpload();
    
    // Add smooth scrolling to navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                scrollToSection(href.substring(1));
            }
        });
    });
    
    // Add CSS for additional styling
    const style = document.createElement('style');
    style.textContent = `
        .risk-level {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .risk-level.low { background-color: #d4edda; color: #155724; }
        .risk-level.medium { background-color: #fff3cd; color: #856404; }
        .risk-level.high { background-color: #f8d7da; color: #721c24; }
        
        .clauses-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .clause-item {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            background: white;
        }
        .clause-type {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            float: right;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});
