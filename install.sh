#!/bin/bash

echo "========================="
echo " Installing Sounix"
echo "========================="

if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed."
    exit 1
fi

echo "Python detected."

python3 -m venv venv

echo "Installing Python packages..."

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Sounix installation complete!"
echo ""
echo "Run Sounix with:"
echo "source venv/bin/activate"
echo "python3 gui.py"
