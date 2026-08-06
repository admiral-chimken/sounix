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
echo "Creating Sounix launcher..."

cat > sounix <<EOF
#!/bin/bash
cd "$(dirname "\$0")"
source venv/bin/activate
python3 app/gui.py
EOF

chmod +x sounix

echo ""
echo "Sounix installation complete!"
echo ""
echo "Launch with:"
echo "./sounix"
