#!/bin/bash

# Setup script for DOCX Feature Extraction System
# This script installs all dependencies and sets up the environment

set -e  # Exit on error

echo "=========================================="
echo "DOCX Feature Extraction System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Check if Ollama is installed
echo ""
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    ollama_version=$(ollama --version 2>&1 || echo "unknown")
    echo "  Version: $ollama_version"
else
    echo "⚠️  Ollama is not installed"
    echo ""
    echo "To install Ollama:"
    echo "  macOS/Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Or visit: https://ollama.com/download"
fi

# Check if Ollama is running
echo ""
echo "Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not running"
    echo ""
    echo "To start Ollama:"
    echo "  ollama serve"
fi

# Check for models
echo ""
echo "Checking for Ollama models..."
if command -v ollama &> /dev/null; then
    models=$(ollama list 2>&1 || echo "")

    if echo "$models" | grep -q "llama3.1:8b\|mistral:7b-instruct\|qwen2.5:7b"; then
        echo "✓ At least one compatible model found"
        echo "$models" | grep "llama3.1:8b\|mistral:7b-instruct\|qwen2.5:7b"
    else
        echo "⚠️  No compatible models found"
        echo ""
        echo "To download a model (choose one):"
        echo "  ollama pull llama3.1:8b        (recommended, 4.7GB)"
        echo "  ollama pull mistral:7b-instruct (fast, 4.1GB)"
        echo "  ollama pull qwen2.5:7b         (structured data, 4.4GB)"
    fi
fi

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p output
echo "✓ Output directory created"

# Run tests
echo ""
echo "Running tests..."
python test_pipeline.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. Ensure Ollama is running: ollama serve"
echo "  2. Process a document: python main.py your_resume.docx"
echo "  3. View examples: python example_usage.py"
echo ""
echo "For help: python main.py --help"
echo ""

