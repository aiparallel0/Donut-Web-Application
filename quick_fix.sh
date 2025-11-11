#!/bin/bash

# Quick Fix Shell Script for DONUT Receipt Parser (Linux/Mac)
# This script runs the fixed donut_minimal.py

echo "============================================================"
echo "DONUT Receipt Parser - Quick Fix"
echo "============================================================"
echo
echo "This script will:"
echo "1. Clear Hugging Face cache (if needed)"
echo "2. Run the fixed donut_minimal.py"
echo

# Option to clear cache
read -p "Clear Hugging Face cache? (y/n): " CLEAR_CACHE
if [[ "$CLEAR_CACHE" =~ ^[Yy]$ ]]; then
    echo "Clearing cache..."
    rm -rf ~/.cache/huggingface/
    echo "Cache cleared."
    echo
fi

echo "Running donut_minimal.py..."
echo
python3 donut_minimal.py

if [ $? -ne 0 ]; then
    echo
    echo "============================================================"
    echo "ERROR: Script failed to run"
    echo "============================================================"
    echo
    echo "Troubleshooting:"
    echo "1. Ensure Python is installed: python3 --version"
    echo "2. Install dependencies: pip3 install -r requirements.txt"
    echo "3. Check the error messages above"
    echo
    exit 1
fi
