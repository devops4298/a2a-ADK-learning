#!/bin/bash

# COM Insurance Confluence Knowledge Agent Setup Script
# This script sets up the production environment for the agent

set -e  # Exit on any error

echo "🚀 COM Insurance Confluence Knowledge Agent Setup"
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.9 or higher and try again."
    exit 1
}

# Check if we're in the right directory
if [ ! -f "confluence_knowledge_agent/agent.py" ]; then
    echo "❌ Please run this script from the project root directory."
    exit 1
fi

echo "✅ Python version check passed"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt || {
    echo "❌ Failed to install dependencies."
    echo "Please check your Python environment and try again."
    exit 1
}

echo "✅ Dependencies installed successfully"

# Check for Google API key
echo "🔑 Checking environment variables..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set."
    echo "Please set your Google API key:"
    echo "export GOOGLE_API_KEY='your-api-key-here'"
    echo ""
    echo "You can get an API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ GOOGLE_API_KEY is set"
fi

# Check Chrome installation
echo "🌐 Checking Chrome installation..."
if command -v google-chrome >/dev/null 2>&1 || command -v chrome >/dev/null 2>&1 || [ -d "/Applications/Google Chrome.app" ]; then
    echo "✅ Chrome is installed"
else
    echo "⚠️  Chrome not found. Please install Google Chrome for authentication."
fi

# Create data directory
echo "📁 Setting up data directory..."
mkdir -p confluence_data
echo "✅ Data directory created"

# Test the CLI
echo "🧪 Testing CLI..."
python3 -m confluence_knowledge_agent.cli --help >/dev/null || {
    echo "❌ CLI test failed. Please check the installation."
    exit 1
}

echo "✅ CLI test passed"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set your Google API key (if not already set):"
echo "   export GOOGLE_API_KEY='your-api-key-here'"
echo ""
echo "2. Log into Confluence in Chrome:"
echo "   Open https://COMinsurence.atlassian.net in Chrome"
echo ""
echo "3. Scrape the Confluence data:"
echo "   python3 -m confluence_knowledge_agent.cli scrape"
echo ""
echo "4. Start the agent:"
echo "   python3 -m confluence_knowledge_agent.cli serve"
echo ""
echo "5. Access the agent at http://localhost:8080"
echo ""
echo "For help, run: python3 -m confluence_knowledge_agent.cli --help"
