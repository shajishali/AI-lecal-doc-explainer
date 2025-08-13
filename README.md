# AI Legal Explainer

An AI-powered legal document analysis platform that transforms complex legal documents into plain language with risk assessment, clause detection, and interactive Q&A capabilities.

## 🚀 Features

### Phase 1 (MVP) - Complete ✅
- **Document Processing**: Upload and process PDF, DOCX, and TXT files
- **AI Summarization**: Generate plain-language summaries using T5 models
- **Clause Detection**: Automatically identify legal clauses and assess risk levels
- **Risk Analysis**: Color-coded risk indicators (🔴🟠🟢) with detailed explanations
- **Interactive Q&A**: Ask questions about documents using Google Gemini API
- **Legal Glossary**: Comprehensive legal terms database with plain-language explanations
- **Responsive UI**: Modern Bootstrap 5 interface with drag-and-drop functionality

### Planned Features (Future Phases)
- **Multilingual Support**: Tamil and Sinhala language models
- **Risk Visualization**: Interactive charts and heatmaps
- **What-If Simulation**: Clause editing and risk recalculation
- **Offline Mode**: Local AI inference capabilities

## 🛠️ Technology Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: MySQL (with SQLite fallback for development)
- **AI/ML**: HuggingFace Transformers (T5), Google Gemini API
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **File Processing**: PyPDF2, python-docx
- **Deployment**: AWS-ready configuration

## 📋 Prerequisites

- Python 3.8+
- MySQL Server (or use SQLite for development)
- Google Gemini API key (for Q&A functionality)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AI_Legal
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv AI_Legal_Explainer_env
AI_Legal_Explainer_env\Scripts\activate

# macOS/Linux
python3 -m venv AI_Legal_Explainer_env
source AI_Legal_Explainer_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=ai_legal_explainer
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# AI Model Settings
AI_MODEL_PATH=./ai_models
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 5. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE ai_legal_explainer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Or use the provided script
python database_config.py
```

### 6. Run Migrations
```bash
cd AI_Legal_Explainer
python manage.py makemigrations
python manage.py migrate
```

### 7. Setup Initial Data
```bash
python manage.py setup_initial_data
```

### 8. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 9. Run the Development Server
```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to access the application.

## 📁 Project Structure

```
AI_Legal/
├── AI_Legal_Explainer/          # Django project
│   ├── AI_Legal_Explainer/      # Project settings
│   ├── main/                    # Main application
│   │   ├── models.py           # Database models
│   │   ├── views.py            # API views and traditional views
│   │   ├── serializers.py      # REST API serializers
│   │   ├── ai_services.py      # AI processing services
│   │   ├── admin.py            # Django admin interface
│   │   ├── templates/          # HTML templates
│   │   └── management/         # Custom management commands
│   └── manage.py               # Django management script
├── requirements.txt             # Python dependencies
├── database_config.py          # Database setup script
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## 🔧 Configuration

### Database Configuration
The application supports both MySQL and SQLite:
- **MySQL**: Configure in `.env` file for production
- **SQLite**: Automatic fallback for development

### AI Model Configuration
- **T5 Model**: Automatically downloads on first use
- **Google Gemini**: Required for Q&A functionality
- **Local Models**: Stored in `AI_MODEL_PATH` directory

### File Upload Settings
- **Max Size**: 10MB (configurable in settings)
- **Supported Formats**: PDF, DOCX, TXT
- **Storage**: Local file system (configurable for S3)

## 📚 API Endpoints

### Documents
- `GET /api/documents/` - List all documents
- `POST /api/documents/` - Upload new document
- `GET /api/documents/{id}/` - Get document details
- `POST /api/documents/{id}/process/` - Process document with AI

### Analysis
- `GET /api/documents/{id}/clauses/` - Get detected clauses
- `GET /api/documents/{id}/risk-analysis/` - Get risk analysis
- `GET /api/documents/{id}/summary/` - Get document summary

### Chat
- `POST /api/chat/ask/` - Ask question about document
- `GET /api/chat/history/` - Get chat session history

### Legal Terms
- `GET /api/legal-terms/` - List all legal terms
- `GET /api/legal-terms/search/` - Search legal terms
- `GET /api/legal-terms/highlight/` - Highlight terms in text

## 🎯 Usage Examples

### 1. Upload and Process a Document
```javascript
// Upload document
const formData = new FormData();
formData.append('title', 'Service Agreement');
formData.append('document_type', 'agreement');
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/documents/', {
    method: 'POST',
    body: formData
});

// Process document
const documentId = response.json().id;
await fetch(`/api/documents/${documentId}/process/`, {
    method: 'POST'
});
```

### 2. Ask Questions About a Document
```javascript
const response = await fetch('/api/chat/ask/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        question: 'What are the main risks in this document?',
        document_id: documentId
    })
});
```

### 3. Get Risk Analysis
```javascript
const response = await fetch(`/api/documents/${documentId}/risk-analysis/`);
const riskAnalysis = await response.json();
console.log(`Risk Level: ${riskAnalysis.overall_risk_level}`);
```

## 🔒 Security Features

- **CSRF Protection**: Enabled for all forms
- **File Validation**: Type and size restrictions
- **Input Sanitization**: XSS protection
- **Rate Limiting**: Configurable API limits
- **Environment Variables**: Secure configuration management

## 🚀 Deployment

### AWS Deployment
1. **EC2 Instance**: Deploy Django application
2. **RDS**: MySQL database
3. **S3**: Document storage
4. **CloudFront**: Static file delivery

### Environment Variables for Production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DB_HOST=your-rds-endpoint
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

### Static Files
```bash
python manage.py collectstatic
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### API Testing
Use tools like Postman or curl to test API endpoints:
```bash
# Test document upload
curl -X POST http://localhost:8000/api/documents/ \
  -F "title=Test Document" \
  -F "document_type=contract" \
  -F "file=@test.pdf"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**This tool is for educational purposes only and does not constitute legal advice. Always consult with qualified legal professionals for legal matters.**

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

## 🎉 Acknowledgments

- **HuggingFace**: For the T5 transformer models
- **Google**: For the Gemini API
- **Bootstrap**: For the responsive UI framework
- **Django**: For the robust web framework

---

**AI Legal Explainer** - Making Legal Documents Accessible to Everyone 🚀
