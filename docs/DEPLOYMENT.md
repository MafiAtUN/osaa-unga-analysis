# UNGA Analysis App - Deployment Guide

## Overview

This guide covers deploying the UNGA Analysis App in various environments, from local development to production deployment on cloud platforms.

## Prerequisites

- Python 3.13+
- Virtual environment
- Required system dependencies
- Database files (unga_vector.db, user_auth.db)

## Local Development

### Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd unga-analysis-app

# 2. Run setup script
python setup.py

# 3. Activate virtual environment
source unga80/bin/activate  # On Windows: unga80\Scripts\activate

# 4. Configure environment
cp env.template .env
# Edit .env with your configuration

# 5. Run application
python main.py
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv unga80
source unga80/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp env.template .env
# Edit .env file

# 4. Initialize database
python setup_database.py

# 5. Run application
streamlit run main.py --server.port 8501
```

## Production Deployment

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t unga-analysis-app .

# Run container
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/unga_vector.db:/app/unga_vector.db \
  -v $(pwd)/user_auth.db:/app/user_auth.db \
  unga-analysis-app
```

### Cloud Deployment

#### Azure App Service

1. **Prepare for Azure**
   ```bash
   # Create requirements-azure.txt
   echo "streamlit>=1.28.0" > requirements-azure.txt
   echo "pandas>=2.0.0" >> requirements-azure.txt
   echo "numpy>=1.24.0" >> requirements-azure.txt
   # Add other dependencies...
   ```

2. **Deploy to Azure**
   ```bash
   # Install Azure CLI
   az login
   
   # Create resource group
   az group create --name unga-analysis-rg --location eastus2
   
   # Create App Service plan
   az appservice plan create --name unga-analysis-plan --resource-group unga-analysis-rg --sku P1V2
   
   # Create web app
   az webapp create --name unga-analysis-prod --resource-group unga-analysis-rg --plan unga-analysis-plan --runtime "PYTHON|3.13"
   
   # Deploy code
   az webapp deployment source config-zip --name unga-analysis-prod --resource-group unga-analysis-rg --src deployment.zip
   ```

3. **Configure Environment Variables**
   ```bash
   az webapp config appsettings set --name unga-analysis-prod --resource-group unga-analysis-rg --settings \
     OPENAI_API_KEY=your_key_here \
     ADMIN_EMAIL=islam50@un.org \
     ADMIN_PASSWORD=OSAAKing!
   ```

#### AWS Elastic Beanstalk

1. **Create deployment package**
   ```bash
   # Create .ebextensions/streamlit.config
   mkdir .ebextensions
   cat > .ebextensions/streamlit.config << EOF
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: main.py
   EOF
   ```

2. **Deploy to AWS**
   ```bash
   # Install EB CLI
   pip install awsebcli
   
   # Initialize EB
   eb init
   
   # Create environment
   eb create unga-analysis-prod
   
   # Deploy
   eb deploy
   ```

#### Google Cloud Platform

1. **Deploy to GCP**
   ```bash
   # Install gcloud CLI
   gcloud init
   
   # Create app.yaml
   cat > app.yaml << EOF
   runtime: python313
   env: standard
   
   handlers:
   - url: /.*
     script: auto
   
   env_variables:
     OPENAI_API_KEY: your_key_here
     ADMIN_EMAIL: islam50@un.org
     ADMIN_PASSWORD: OSAAKing!
   EOF
   
   # Deploy
   gcloud app deploy
   ```

### Database Deployment

#### Database Setup
```bash
# 1. Ensure database files exist
ls -la *.db

# 2. Set proper permissions
chmod 644 unga_vector.db user_auth.db

# 3. Backup databases
cp unga_vector.db unga_vector_backup.db
cp user_auth.db user_auth_backup.db
```

#### Database Migration
```python
# Migration script
from src.unga_analysis.data.simple_vector_storage import simple_vector_storage as db_manager

def migrate_database():
    """Migrate database to new schema if needed."""
    try:
        # Check if migration is needed
        db_manager.create_db_and_tables()
        print("Database migration completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()
```

## Environment Configuration

### Production Environment Variables
```env
# OpenAI Configuration
OPENAI_API_KEY=your_production_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Admin Configuration
ADMIN_EMAIL=islam50@un.org
ADMIN_PASSWORD=your_secure_password_here

# Database Configuration
DATABASE_URL=sqlite:///unga_vector.db
USER_DATABASE_URL=sqlite:///user_auth.db

# Security
SECRET_KEY=your_production_secret_key_here
SESSION_TIMEOUT=3600

# Application
DEBUG=False
LOG_LEVEL=INFO
```

### SSL Configuration
```nginx
# Nginx configuration for SSL
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Logging

### Application Monitoring
```python
# Add to main.py
import logging
from src.unga_analysis.config.logging import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Monitor application health
def health_check():
    """Check application health."""
    try:
        # Check database connection
        db_manager.conn.execute("SELECT 1").fetchone()
        
        # Check authentication system
        auth_manager = UserAuthManager()
        
        logger.info("Health check passed")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

### Log Management
```bash
# Set up log rotation
sudo cat > /etc/logrotate.d/unga-analysis << EOF
/var/log/unga-analysis/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF
```

## Security Considerations

### Production Security
1. **Environment Variables**: Never commit .env files
2. **Database Security**: Use proper file permissions
3. **API Keys**: Rotate keys regularly
4. **Access Control**: Implement proper user authentication
5. **HTTPS**: Always use SSL in production

### Security Checklist
- [ ] Environment variables secured
- [ ] Database files protected
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Access logs monitored

## Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_speeches_country_year ON speeches(country_name, year);
CREATE INDEX idx_speeches_text ON speeches(speech_text);
CREATE INDEX idx_speeches_embedding ON speeches(embedding);
```

### Application Optimization
```python
# Enable caching
import streamlit as st

@st.cache_data
def get_countries():
    """Cache country list for performance."""
    return country_manager.get_all_countries()

@st.cache_data
def search_speeches(query, countries, years):
    """Cache search results."""
    return db_manager.search_speeches(
        query_text=query,
        countries=countries,
        years=years
    )
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8501
   lsof -i :8501
   # Kill process
   kill -9 <PID>
   ```

2. **Database Locked**
   ```bash
   # Check database permissions
   ls -la *.db
   # Fix permissions
   chmod 644 *.db
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   top -p $(pgrep -f streamlit)
   # Increase memory limit
   export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
   ```

### Debug Mode
```bash
# Run in debug mode
streamlit run main.py --server.port 8501 --logger.level debug
```

## Backup and Recovery

### Database Backup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp unga_vector.db "backups/unga_vector_$DATE.db"
cp user_auth.db "backups/user_auth_$DATE.db"
echo "Backup completed: $DATE"
EOF

chmod +x backup.sh
```

### Recovery Process
```bash
# Restore from backup
cp backups/unga_vector_20240101_120000.db unga_vector.db
cp backups/user_auth_20240101_120000.db user_auth.db
```

## Support

For deployment support:
- **Email**: islam50@un.org
- **Documentation**: See `docs/` directory
- **Issues**: Create an issue in the repository

---

**🚀 UNGA Analysis App - Production-Ready Deployment**