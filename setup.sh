#!/bin/bash

echo "Setting up Azure Cost Optimizer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed! Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed! Please install pip."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
python -m pip install --upgrade pip
pip install wheel

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please edit the .env file with your Azure credentials."
fi

echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Edit the .env file with your Azure credentials"
echo "2. Run 'python main.py' to start the application"
echo
