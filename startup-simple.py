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
    
    # Install requirements first
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-simple.txt'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        # Continue anyway
    
    # Start Streamlit with the simple app
    cmd = [sys.executable, '-m', 'streamlit', 'run', 'app-simple.py', '--server.port=8000', '--server.address=0.0.0.0']
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
