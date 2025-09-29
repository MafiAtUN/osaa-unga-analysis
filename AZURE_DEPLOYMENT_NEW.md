# 🚀 Azure Deployment Guide - New Framework

## Overview

This guide covers deploying the new, refactored UN GA Daily Readouts application to Azure App Service. The new framework provides:

- **Modular Architecture**: Clean separation of concerns
- **Professional Structure**: Well-organized, maintainable code
- **Enhanced Security**: Comprehensive security measures
- **Better Performance**: Optimized for production

## 📁 New Framework Structure

```
osaa-unga-80/
├── src/                          # Main application code
│   ├── app.py                    # Main application (clean, minimal)
│   ├── config/                   # Configuration management
│   │   ├── settings.py           # Application settings
│   │   └── __init__.py
│   ├── core/                     # Core business logic
│   │   ├── security/             # Security modules
│   │   │   ├── authentication.py
│   │   │   ├── input_validation.py
│   │   │   ├── rate_limiting.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── ui/                       # User interface
│   │   ├── components/           # Reusable UI components
│   │   │   ├── file_upload.py
│   │   │   ├── navigation.py
│   │   │   └── __init__.py
│   │   ├── pages/                # Page layouts
│   │   │   ├── dashboard.py
│   │   │   ├── analysis.py
│   │   │   ├── history.py
│   │   │   ├── settings.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── services/                 # External services
│   │   ├── file_processing/      # File handling
│   │   ├── llm/                  # LLM integration
│   │   ├── storage/              # Database operations
│   │   └── __init__.py
│   └── __init__.py
├── app_new.py                    # New main entry point
├── requirements.txt              # Dependencies
├── web.config                    # Azure configuration
└── startup.sh                    # Startup script
```

## 🔧 Azure Deployment Steps

### 1. Prepare for Deployment

```bash
# Ensure you're in the project directory
cd /Users/mafilicious/osaa-unga-80

# Test the new application locally first
streamlit run app_new.py
```

### 2. Update Azure App Service

#### Option A: Git Deployment (Recommended)

```bash
# Add Azure remote (if not already added)
git remote add azure https://your-app.scm.azurewebsites.net/your-app.git

# Commit the new framework
git add .
git commit -m "Implement new professional framework structure"
git push azure main
```

#### Option B: ZIP Deployment

```bash
# Create deployment package (excluding old files)
zip -r app-deployment-new.zip . \
  -x "app.py" \
  -x "app_backup.py" \
  -x "*.pyc" \
  -x "__pycache__/*" \
  -x "*.git*" \
  -x "osaaunga/*"

# Upload via Azure Portal
```

### 3. Update Startup Command

In Azure Portal → App Service → Configuration → General Settings:

**Startup Command:**
```bash
streamlit run app_new.py --server.port $PORT --server.address 0.0.0.0
```

### 4. Environment Variables

Ensure these environment variables are set in Azure Portal:

```bash
# Required
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
APP_PASSWORD=your-secure-password

# Optional
RATE_LIMIT_ATTEMPTS=5
RATE_LIMIT_WINDOW=300
MAX_FILE_SIZE=52428800
LOG_LEVEL=INFO
```

### 5. Update requirements.txt

The new framework uses the same dependencies, but ensure your `requirements.txt` includes:

```txt
streamlit>=1.28.0
openai>=1.43.0
pypdf>=3.15.0
pdfminer.six>=20221105
python-docx>=0.8.11
pydub>=0.25.1
sqlalchemy>=2.0.0
tiktoken>=0.5.0
langdetect>=1.0.9
python-dotenv>=1.0.0
python-multipart>=0.0.6
requests>=2.31.0
```

## 🚀 Deployment Commands

### Quick Deployment

```bash
# 1. Test locally
streamlit run app_new.py

# 2. Commit changes
git add .
git commit -m "Deploy new professional framework"

# 3. Deploy to Azure
git push azure main
```

### Verification

After deployment, verify:

1. **Application loads** at your Azure URL
2. **Authentication works** with your password
3. **File upload** functionality works
4. **Analysis generation** works
5. **Database operations** work
6. **Security features** are active

## 🔒 Security Features

The new framework includes enhanced security:

- ✅ **API Key Protection**: No keys in session state
- ✅ **Input Sanitization**: All inputs validated
- ✅ **Rate Limiting**: Protection against brute force
- ✅ **File Validation**: Secure file uploads
- ✅ **Prompt Safety**: LLM injection protection

## 📊 Benefits of New Framework

### **Maintainability**
- **Modular Structure**: Easy to find and modify code
- **Clear Separation**: UI, business logic, and services separated
- **Professional Organization**: Industry-standard structure

### **Security**
- **Comprehensive Protection**: All major vulnerabilities addressed
- **Input Validation**: Sanitized and validated inputs
- **Rate Limiting**: Protection against abuse

### **Performance**
- **Optimized Code**: Clean, efficient implementation
- **Better Error Handling**: Graceful failure management
- **Improved Logging**: Better debugging and monitoring

### **Scalability**
- **Plugin Architecture**: Easy to add new features
- **Service-Oriented**: Microservices-ready structure
- **Configuration Management**: Environment-specific settings

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure all __init__.py files exist
   find src -type d -exec touch {}/__init__.py \;
   ```

2. **Module Not Found**
   ```bash
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Configuration Errors**
   ```bash
   # Verify environment variables
   echo $AZURE_OPENAI_API_KEY
   echo $APP_PASSWORD
   ```

### Logs

Check Azure App Service logs:
```bash
az webapp log tail --name your-app-name --resource-group your-resource-group
```

## 📈 Performance Optimization

### Azure App Service Settings

- **Plan**: B1 or higher for production
- **Always On**: Enabled for better performance
- **Auto Scale**: Configure based on usage
- **Health Check**: Monitor application health

### Monitoring

- **Application Insights**: Enable for monitoring
- **Log Analytics**: Track application logs
- **Metrics**: Monitor performance metrics

## 🔄 Rollback Plan

If issues occur, rollback to previous version:

```bash
# Rollback to previous commit
git revert HEAD
git push azure main

# Or rollback to specific tag
git checkout security-fixed-20250929-100105
git push azure main --force
```

## ✅ Deployment Checklist

- [ ] New framework tested locally
- [ ] All dependencies updated
- [ ] Environment variables configured
- [ ] Startup command updated
- [ ] Security features verified
- [ ] Performance tested
- [ ] Monitoring configured
- [ ] Rollback plan ready

---

**The new framework provides a professional, maintainable, and secure foundation for the UN GA Daily Readouts application!** 🎉
