#!/bin/bash
# Clean Azure Deployment Script for UNGA Speech Analysis App
# This script creates a clean deployment with proper naming and East US 2 region

set -e  # Exit on any error

echo "🚀 Starting Clean Azure Deployment for UNGA Speech Analysis App"
echo "================================================================"

# Configuration - Clean, readable names as requested
RESOURCE_GROUP="unga-speech-analysis"
APP_NAME="unga-speech-analysis"
PLAN_NAME="unga-speech-analysis-plan"
LOCATION="East US 2"
PYTHON_VERSION="3.9"
SKU="B2"  # Better compute power for efficiency

echo "📋 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Name: $APP_NAME"
echo "   Plan Name: $PLAN_NAME"
echo "   Location: $LOCATION"
echo "   Python Version: $PYTHON_VERSION"
echo "   SKU: $SKU (Better compute power)"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

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

echo "✅ Prerequisites check passed"
echo ""

# Clean up any existing resources (optional - uncomment if needed)
# echo "🧹 Cleaning up any existing resources..."
# az group delete --name $RESOURCE_GROUP --yes --no-wait 2>/dev/null || true
# sleep 10

# Create resource group
echo "🏗️  Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create App Service plan with better SKU
echo "📦 Creating App Service plan: $PLAN_NAME"
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku $SKU \
    --is-linux \
    --output table

# Create web app
echo "🌐 Creating web app: $APP_NAME"
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --runtime "PYTHON|$PYTHON_VERSION" \
    --output table

# Configure app settings for optimal performance
echo "⚙️  Configuring app settings for optimal performance..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true \
        ENABLE_ORYX_BUILD=true \
        WEBSITES_PORT=8000 \
        PYTHONPATH=/home/site/wwwroot \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Set startup command to use the simple app
echo "🚀 Setting startup command to use app-simple.py..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup-simple.py"

# Create a simple startup script for the simple app
echo "📝 Creating startup script for simple app..."
cat > startup-simple.py << 'EOF'
#!/usr/bin/env python3
"""
Azure App Service startup script for UNGA Analysis App (Simple Version)
"""
import os
import sys
import subprocess

def main():
    # Set environment variables for Azure
    os.environ['STREAMLIT_SERVER_PORT'] = '8000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Change to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Start Streamlit with the simple app
    cmd = [sys.executable, '-m', 'streamlit', 'run', 'app-simple.py', '--server.port=8000', '--server.address=0.0.0.0']
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
EOF

echo "✅ Azure resources created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Your app will be available at:"
echo "   https://$APP_NAME.azurewebsites.net"
echo ""
echo "2. To deploy your code, run:"
echo "   git remote add azure https://$APP_NAME.scm.azurewebsites.net/$APP_NAME.git"
echo "   git push azure main"
echo ""
echo "3. To set environment variables (if needed):"
echo "   az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings APP_PASSWORD='your-password'"
echo ""
echo "🎉 Deployment completed! Your UNGA Speech Analysis App is ready!"
echo "   URL: https://$APP_NAME.azurewebsites.net"
