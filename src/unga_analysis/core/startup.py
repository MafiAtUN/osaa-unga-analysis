#!/usr/bin/env python3
"""
Azure App Service startup script for UNGA Analysis App
"""

import os
import sys
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the Streamlit app for Azure App Service."""
    try:
        # Get port from environment variable (Azure sets this)
        port = os.environ.get('PORT', '8502')
        
        # Start Streamlit app
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', port,
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'false',
            '--server.runOnSave', 'false'
        ]
        
        print(f"Starting Streamlit app on port {port}")
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        print(f"Failed to start app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
