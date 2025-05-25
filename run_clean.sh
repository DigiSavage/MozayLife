#!/bin/bash
# Cleans all .pyc and .DS_Store files recursively in the project

clean_pyc() {
    echo "Removing *.pyc files..."
    find . -name "*.pyc" -exec rm -rf {} \;
    echo "Removing .DS_Store files..."
    find . -name ".DS_Store" -exec rm -rf {} \;
    echo "Removing AppleDouble files (._.DS_Store)..."
    find . -name "._.DS_Store" -exec rm -rf {} \;
    echo "Clean complete!"
}

clean_pyc