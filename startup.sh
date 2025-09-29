#!/bin/bash

# Azure App Service startup script for Streamlit
# This script starts the Streamlit app on Azure

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:${HOME}/site/wwwroot"

# Install any missing dependencies
pip install -r requirements-azure.txt

# Start Streamlit with Azure-compatible settings
streamlit run app.py \
    --server.port 8000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false

