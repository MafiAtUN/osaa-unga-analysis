# 🚀 Azure Deployment Guide for UNGA Analysis App

This guide will help you deploy the UNGA Analysis App to Azure App Service.

## 📋 Prerequisites

1. **Azure CLI** installed and configured
2. **Git** installed
3. **Azure subscription** with appropriate permissions
4. **Environment variables** ready (Azure OpenAI credentials)

## 🛠️ Deployment Options

### Option 1: Automated Deployment (Recommended)

Run the automated deployment script:

```bash
./azure-deploy.sh
```

This script will:
- Create a resource group
- Create an App Service plan
- Create a web app
- Configure all necessary settings

### Option 2: Manual Deployment

#### Step 1: Create Azure Resources

```bash
# Set your variables
RESOURCE_GROUP="unga-analysis-rg"
APP_NAME="unga-analysis-app"
LOCATION="East US"
PLAN_NAME="unga-analysis-plan"

# Create resource group
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service plan
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux

# Create web app
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --runtime "PYTHON|3.9"
```

#### Step 2: Configure App Settings

```bash
# Set environment variables
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        AZURE_OPENAI_API_KEY="your-azure-openai-api-key" \
        AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com/" \
        APP_PASSWORD="your-secure-password" \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true
```

#### Step 3: Set Startup Command

```bash
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup.py"
```

#### Step 4: Deploy Code

```bash
# Add Azure remote
git remote add azure https://$APP_NAME.scm.azurewebsites.net/$APP_NAME.git

# Deploy to Azure
git push azure main
```

## 🔧 Environment Variables

Set these in Azure Portal or via CLI:

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint | `https://your-resource.cognitiveservices.azure.com/` |
| `APP_PASSWORD` | Password for app access | `your-secure-password` |

## 📁 Deployment Files

The following files are included for Azure deployment:

- `web.config` - IIS configuration for Windows App Service
- `startup.py` - Python startup script for Azure
- `.deployment` - Deployment configuration
- `azure-deploy.sh` - Automated deployment script

## 🌐 Accessing Your App

After deployment, your app will be available at:
```
https://your-app-name.azurewebsites.net
```

## 🔍 Troubleshooting

### Common Issues

1. **App won't start**
   - Check startup command is set to `startup.py`
   - Verify Python version is 3.9
   - Check logs in Azure Portal

2. **Environment variables not working**
   - Verify variables are set in App Settings
   - Check variable names match exactly
   - Restart the app after setting variables

3. **Database issues**
   - The app uses DuckDB which works well in Azure
   - Database file is stored in the app's file system
   - Consider Azure Database for production use

### Viewing Logs

```bash
# Stream logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP
```

## 💰 Cost Optimization

- **App Service Plan**: Start with B1 (Basic) for testing
- **Scaling**: Use auto-scaling for production
- **Storage**: App Service includes 1GB free storage
- **Database**: Consider Azure Database for larger datasets

## 🔒 Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Enabled by default on Azure App Service
3. **Authentication**: App includes password protection
4. **CORS**: Configured for Azure deployment

## 📊 Monitoring

- **Application Insights**: Enable for monitoring
- **Health Checks**: Built into the app
- **Performance**: Monitor via Azure Portal

## 🚀 Production Deployment

For production deployment:

1. **Use Production SKU**: P1V2 or higher
2. **Enable SSL**: Configure custom domain
3. **Set up Monitoring**: Application Insights
4. **Database**: Consider Azure Database
5. **CDN**: Use Azure CDN for static assets

## 📞 Support

If you encounter issues:

1. Check Azure Portal logs
2. Verify environment variables
3. Test locally first
4. Check Azure status page

---

**Ready to deploy? Run `./azure-deploy.sh` to get started!** 🚀

