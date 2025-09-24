#!/usr/bin/env python3
"""
Setup script to create .env file with Azure OpenAI configuration.
This script will create a .env file with your Azure OpenAI credentials.
"""

import os

def create_env_file():
    """Create .env file with Azure OpenAI configuration."""
    
    # Azure OpenAI configuration template
    azure_config = """# Azure OpenAI Configuration
# Replace with your actual API key
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
"""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Create .env file
    try:
        with open('.env', 'w') as f:
            f.write(azure_config)
        print("✅ .env file created successfully!")
        print("🔒 Your API key is now stored locally and will be ignored by Git.")
        print("📝 You can now run: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    print("🔧 Setting up Azure OpenAI configuration...")
    create_env_file()
