#!/bin/bash
# Azure Deployment Script for UNGA Analysis App

echo "🚀 Starting Azure deployment for UNGA Analysis App..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure CLI:"
    az login
fi

# Set variables (modify these for your deployment)
RESOURCE_GROUP="unga-analysis-rg"
APP_NAME="unga-analysis-app"
LOCATION="North Europe"
PLAN_NAME="unga-analysis-plan"
PYTHON_VERSION="3.9"

echo "📋 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Name: $APP_NAME"
echo "   Location: $LOCATION"
echo "   Python Version: $PYTHON_VERSION"

# Create resource group
echo "🏗️  Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service plan
echo "📦 Creating App Service plan..."
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux

# Create web app
echo "🌐 Creating web app..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --runtime "PYTHON|3.9"

# Configure app settings
echo "⚙️  Configuring app settings..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true

# Set startup command
echo "🚀 Setting startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup.py"

echo "✅ Azure resources created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Set your environment variables in Azure Portal:"
echo "   - AZURE_OPENAI_API_KEY"
echo "   - AZURE_OPENAI_ENDPOINT"
echo "   - APP_PASSWORD"
echo ""
echo "2. Deploy your code:"
echo "   git remote add azure https://$APP_NAME.scm.azurewebsites.net/$APP_NAME.git"
echo "   git push azure main"
echo ""
echo "3. Your app will be available at:"
echo "   https://$APP_NAME.azurewebsites.net"
echo ""
echo "🔧 To set environment variables via CLI:"
echo "az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings AZURE_OPENAI_API_KEY='your-key' AZURE_OPENAI_ENDPOINT='your-endpoint' APP_PASSWORD='your-password'"
