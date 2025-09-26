# Azure Deployment Guide for OSAA UN GA Analysis App

## 🚀 Quick Deployment

### Prerequisites
1. **Azure CLI** installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Azure account** with appropriate permissions
3. **Git** (optional, for alternative deployment methods)

### Method 1: Automated Script (Recommended)

```bash
# Make the script executable and run it
chmod +x azure-deploy.sh
./azure-deploy.sh
```

### Method 2: Manual Azure CLI Commands

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name osaa-unga-analysis-rg --location "East US 2"

# 3. Create App Service plan
az appservice plan create \
    --name osaa-unga-analysis-plan \
    --resource-group osaa-unga-analysis-rg \
    --sku B1 \
    --is-linux

# 4. Create web app
az webapp create \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --plan osaa-unga-analysis-plan \
    --runtime "PYTHON|3.11"

# 5. Configure environment variables
az webapp config appsettings set \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --settings \
        AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_API_KEY" \
        AZURE_OPENAI_ENDPOINT="YOUR_AZURE_OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
        WHISPER_API_KEY="YOUR_WHISPER_API_KEY" \
        WHISPER_ENDPOINT="YOUR_WHISPER_ENDPOINT" \
        WHISPER_API_VERSION="2024-06-01"

# 6. Configure startup command
az webapp config set \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --startup-file "streamlit run app.py --server.port 8000 --server.address 0.0.0.0"

# 7. Deploy application
zip -r app-deployment.zip . -x "osaaunga/*" "__pycache__/*" "*.pyc" ".git/*" "*.db" ".env"
az webapp deployment source config-zip \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --src app-deployment.zip
```

## 📋 Configuration Details

### Resource Group
- **Name**: `osaa-unga-analysis-rg`
- **Location**: East US 2
- **Purpose**: Contains all resources for the OSAA UN GA Analysis app

### App Service
- **Name**: `osaa-unga-analysis`
- **URL**: `https://osaa-unga-analysis.azurewebsites.net`
- **Runtime**: Python 3.11
- **Plan**: B1 (Basic tier)

### Environment Variables
The following environment variables are automatically configured:

| Variable | Value | Purpose |
|----------|-------|---------|
| `AZURE_OPENAI_API_KEY` | Your Chat Completions API key | Text analysis |
| `AZURE_OPENAI_ENDPOINT` | Chat Completions endpoint | Text analysis |
| `AZURE_OPENAI_API_VERSION` | 2024-12-01-preview | API version |
| `WHISPER_API_KEY` | Your Whisper API key | Audio transcription |
| `WHISPER_ENDPOINT` | Whisper endpoint | Audio transcription |
| `WHISPER_API_VERSION` | 2024-06-01 | Whisper API version |

## 🔧 Post-Deployment

### Monitor Your App
```bash
# View logs
az webapp log tail --name osaa-unga-analysis --resource-group osaa-unga-analysis-rg

# Check app status
az webapp show --name osaa-unga-analysis --resource-group osaa-unga-analysis-rg
```

### Update App Settings
```bash
az webapp config appsettings set \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --settings KEY=VALUE
```

### Redeploy
```bash
# Create new deployment package
zip -r app-deployment.zip . -x "osaaunga/*" "__pycache__/*" "*.pyc" ".git/*" "*.db" ".env"

# Deploy
az webapp deployment source config-zip \
    --name osaa-unga-analysis \
    --resource-group osaa-unga-analysis-rg \
    --src app-deployment.zip
```

## 🌐 Access Your App

Once deployed, your app will be available at:
**https://osaa-unga-analysis.azurewebsites.net**

## 🛠️ Troubleshooting

### Common Issues

1. **App won't start**
   - Check logs: `az webapp log tail --name osaa-unga-analysis --resource-group osaa-unga-analysis-rg`
   - Verify environment variables are set correctly

2. **API errors**
   - Ensure API keys are correct and have proper permissions
   - Check that endpoints are accessible from Azure

3. **Performance issues**
   - Consider upgrading to a higher App Service plan (S1, P1, etc.)
   - Monitor resource usage in Azure Portal

### Log Locations
- **Application logs**: Available via Azure Portal or CLI
- **Streamlit logs**: Check startup.sh output
- **Error logs**: Azure App Service logs

## 💰 Cost Optimization

- **B1 Plan**: ~$13/month (Basic tier)
- **S1 Plan**: ~$55/month (Standard tier) - for production
- **P1 Plan**: ~$219/month (Premium tier) - for high traffic

## 🔒 Security Notes

- API keys are stored as App Service application settings (encrypted at rest)
- No sensitive data is exposed in the codebase
- HTTPS is enabled by default
- Consider adding custom domain and SSL certificate for production

## 📞 Support

For deployment issues:
1. Check Azure App Service logs
2. Verify all environment variables
3. Ensure all dependencies are in requirements-azure.txt
4. Check that the startup command is correct
