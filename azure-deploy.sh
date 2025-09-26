#!/bin/bash

# Azure Deployment Script for OSAA UN GA Analysis App
# This script creates the resource group, app service, and deploys the application

set -e

# Configuration
RESOURCE_GROUP="osaa-unga-analysis-rg"
APP_NAME="osaa-unga-analysis"
LOCATION="East US 2"
PLAN_NAME="osaa-unga-analysis-plan"
SKU="B1"

echo "🚀 Starting Azure deployment for OSAA UN GA Analysis App..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure:"
    az login
fi

echo "📋 Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION"

echo "📦 Creating App Service plan: $PLAN_NAME"
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux

echo "🌐 Creating web app: $APP_NAME"
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --runtime "PYTHON|3.11"

echo "⚙️  Configuring app settings..."

# Set environment variables (replace with your actual values)
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        AZURE_OPENAI_API_KEY="YOUR_AZURE_OPENAI_API_KEY" \
        AZURE_OPENAI_ENDPOINT="YOUR_AZURE_OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
        WHISPER_API_KEY="YOUR_WHISPER_API_KEY" \
        WHISPER_ENDPOINT="YOUR_WHISPER_ENDPOINT" \
        WHISPER_API_VERSION="2024-06-01"

echo "🔧 Configuring startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "streamlit run app.py --server.port 8000 --server.address 0.0.0.0"

echo "📁 Deploying application files..."
# Create deployment package
zip -r app-deployment.zip . -x "osaaunga/*" "__pycache__/*" "*.pyc" ".git/*" "*.db" ".env"

# Deploy using zip deployment
az webapp deployment source config-zip \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src app-deployment.zip

echo "✅ Deployment completed!"
echo "🌐 Your app is available at: https://$APP_NAME.azurewebsites.net"
echo ""
echo "📊 To monitor your app:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🔧 To update app settings:"
echo "   az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings KEY=VALUE"
