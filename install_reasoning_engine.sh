#!/bin/bash

# Candidate Screening Reasoning Engine - Installation Script
# This script helps set up the reasoning engine environment

set -e  # Exit on error

echo "================================================"
echo "Candidate Screening Reasoning Engine - Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo "ℹ $1"
}

# Check Python version
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
    
    # Check if version is 3.8 or higher
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python version is 3.8 or higher"
    else
        print_warning "Python 3.8+ recommended (you have $PYTHON_VERSION)"
    fi
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo ""

# Check pip
echo "Step 2: Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_success "pip3 found: $PIP_VERSION"
else
    print_error "pip3 not found. Please install pip."
    exit 1
fi

echo ""

# Ask if user wants to create virtual environment
echo "Step 3: Virtual environment setup"
read -p "Create a virtual environment? (recommended) [y/N]: " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    VENV_DIR="venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at ./$VENV_DIR"
        read -p "Recreate it? [y/N]: " recreate_venv
        if [[ $recreate_venv =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            python3 -m venv "$VENV_DIR"
            print_success "Virtual environment recreated"
        fi
    else
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at ./$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
else
    print_info "Skipping virtual environment creation"
fi

echo ""

# Install dependencies
echo "Step 4: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    print_info "Installing packages from requirements.txt..."
    pip3 install -r requirements.txt
    print_success "All dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

echo ""

# Setup .env file
echo "Step 5: Environment configuration"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "IMPORTANT: Edit .env file with your Google API credentials"
    else
        print_error ".env.example not found!"
    fi
else
    print_info ".env file already exists (not overwriting)"
fi

echo ""

# Create necessary directories
echo "Step 6: Creating directories..."
mkdir -p output
mkdir -p resumes
print_success "Created output/ and resumes/ directories"

echo ""

# Test imports
echo "Step 7: Testing installations..."
print_info "Testing Python imports..."

python3 << EOF
import sys
try:
    import pandas
    print("✓ pandas")
    import openpyxl
    print("✓ openpyxl")
    from google.oauth2 import service_account
    print("✓ google-auth")
    from googleapiclient.discovery import build
    print("✓ google-api-python-client")
    from dotenv import load_dotenv
    print("✓ python-dotenv")
    print("\n✓ All required packages are installed correctly")
except ImportError as e:
    print(f"\n✗ Import error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "All imports successful"
else
    print_error "Some imports failed. Check error messages above."
    exit 1
fi

echo ""

# Summary
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
print_success "Dependencies installed"
print_success "Directories created"
print_success "Environment configured"
echo ""
echo "Next Steps:"
echo "  1. Edit .env file with your Google API credentials:"
echo "     ${YELLOW}nano .env${NC}"
echo ""
echo "  2. Follow the setup guide:"
echo "     ${YELLOW}cat REASONING_ENGINE_SETUP.md${NC}"
echo ""
echo "  3. Test with sample data:"
echo "     ${YELLOW}python3 reasoning_engine.py -i sample_candidates.json -o test_report.xlsx${NC}"
echo ""
echo "  4. Test Google services:"
echo "     ${YELLOW}python3 google_drive_service.py${NC}"
echo "     ${YELLOW}python3 gmail_service.py${NC}"
echo ""
echo "Documentation:"
echo "  • Quick Reference: QUICK_REFERENCE.md"
echo "  • Setup Guide: REASONING_ENGINE_SETUP.md"
echo "  • Implementation Details: IMPLEMENTATION_SUMMARY.md"
echo ""

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Virtual Environment:"
    echo "  • Activate: ${YELLOW}source venv/bin/activate${NC}"
    echo "  • Deactivate: ${YELLOW}deactivate${NC}"
    echo ""
fi

print_warning "Remember to configure your Google API credentials in .env!"
echo ""
echo "================================================"
