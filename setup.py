#!/usr/bin/env python3
"""
UNGA Analysis App - Setup Script
Production-ready setup for the UNGA Analysis application
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 13):
        print("❌ Python 3.13+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_environment():
    """Set up the virtual environment."""
    if not os.path.exists("unga80"):
        if not run_command("python3 -m venv unga80", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    return True

def install_dependencies():
    """Install required dependencies."""
    if not run_command("source unga80/bin/activate && pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command("source unga80/bin/activate && pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_environment_file():
    """Set up environment configuration."""
    if not os.path.exists(".env"):
        if os.path.exists("env.template"):
            if run_command("cp env.template .env", "Creating .env file from template"):
                print("✅ Environment file created")
                print("⚠️  Please edit .env file with your configuration")
                return True
        else:
            print("❌ env.template not found")
            return False
    else:
        print("✅ Environment file already exists")
        return True

def setup_database():
    """Set up the database."""
    if not run_command("source unga80/bin/activate && python setup_database.py", "Setting up database"):
        return False
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["logs", "artifacts", "tests"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    return True

def main():
    """Main setup function."""
    print("🚀 UNGA Analysis App - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up environment file
    if not setup_environment_file():
        print("❌ Failed to set up environment file")
        sys.exit(1)
    
    # Set up database
    if not setup_database():
        print("❌ Failed to set up database")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: source unga80/bin/activate")
    print("3. Run: python main.py")
    print("\n🌐 The app will be available at: http://localhost:8501")
    print("\n🔐 Default admin credentials:")
    print("   Email: islam50@un.org")
    print("   Password: OSAAKing!")

if __name__ == "__main__":
    main()