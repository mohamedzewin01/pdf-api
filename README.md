# Google Cloud Deployment Guide

## Prerequisites
1. Google Cloud account with billing enabled
2. Google Cloud SDK installed
3. Python 3.9 or higher

## Steps to Deploy

### 1. Install Google Cloud SDK
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use the installer you already have
```

### 2. Initialize and Login
```bash
gcloud init
gcloud auth login
```

### 3. Create a New Project (if needed)
```bash
gcloud projects create your-project-id --name="PDF AI API"
gcloud config set project your-project-id
```

### 4. Enable Required APIs
```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 5. Create App Engine Application
```bash
gcloud app create --region=us-central1
```

### 6. Deploy the Application
```bash
# Navigate to your app directory
cd C:\Users\Zewin\Desktop\app

# Deploy to Google Cloud
gcloud app deploy app.yaml --quiet
```

### 7. View Your Deployed App
```bash
gcloud app browse
```

## Files Structure
```
app/
├── main.py              # Main FastAPI application
├── app.py               # Alternative simple version
├── app.yaml             # Google Cloud configuration
├── requirements.txt     # Python dependencies
├── php_client_example.php # PHP client example
└── README.md           # This file
```

## API Endpoints
- `GET /` - API information
- `POST /upload_pdf/` - Upload PDF file
- `POST /ask/` - Ask question about uploaded PDF
- `GET /health` - Health check
- `GET /status/` - System status
- `DELETE /reset/` - Reset system

## PHP Usage Example
```php
// Replace with your deployed URL
$api_url = 'https://your-project-id.appspot.com';
$client = new PDFAIClient($api_url);

// Upload PDF
$result = $client->uploadPDF('/path/to/file.pdf');

// Ask question
$answer = $client->askQuestion('What is this document about?');
```

## Environment Variables
The app.yaml file includes:
- `GROQ_API_KEY`: Your Groq API key for AI processing

## Troubleshooting

### Common Issues:
1. **Memory Issues**: Increase memory in app.yaml
2. **Timeout**: Increase timeout settings
3. **Dependencies**: Check requirements.txt versions
4. **API Key**: Ensure GROQ_API_KEY is set correctly

### Logs:
```bash
gcloud app logs tail -s default
```

### Update Deployment:
```bash
gcloud app deploy app.yaml --quiet
```

## Testing
1. Test health endpoint: `https://your-project-id.appspot.com/health`
2. Upload a PDF via POST request
3. Ask questions via POST request

## Security Notes
- API key is in environment variables
- File uploads are temporary and cleaned up
- No persistent storage of user data
