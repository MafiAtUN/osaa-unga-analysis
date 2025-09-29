#!/bin/bash

# Azure App Service startup script for Streamlit
# Professional UN GA Daily Readouts Application

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:${HOME}/site/wwwroot"

# Install dependencies from clean requirements.txt
pip install -r requirements.txt

# Start Streamlit with Azure-compatible settings
streamlit run app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false

