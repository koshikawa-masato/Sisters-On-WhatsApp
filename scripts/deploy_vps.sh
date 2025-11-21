#!/bin/bash
# Deploy Sisters-On-WhatsApp to XServer VPS using rsync
# Per CLAUDE.md Rule #3: Use rsync, NOT git clone

set -e  # Exit on error

# VPS Configuration
VPS_ALIAS="xserver-vps"  # SSH config alias
VPS_PATH="/root/Sisters-On-WhatsApp"
LOCAL_PATH="/home/koshikawa/Sisters-On-WhatsApp"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Sisters-On-WhatsApp Deployment${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Step 1: Sync code to VPS (exclude sensitive/unnecessary files)
echo -e "${YELLOW}[1/4] Syncing code to VPS...${NC}"
rsync -avz --delete \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='prompts/' \
  --exclude='diary/' \
  --exclude='CLAUDE.md' \
  --exclude='.gitignore' \
  --exclude='test_*.py' \
  --exclude='*.log' \
  "$LOCAL_PATH/" "${VPS_ALIAS}:${VPS_PATH}/"

echo -e "${GREEN}✓ Code synced${NC}"

# Step 2: Sync prompts separately (gitignored files)
echo -e "${YELLOW}[2/4] Syncing character prompts...${NC}"
if [ -d "$LOCAL_PATH/prompts" ]; then
  rsync -avz \
    "$LOCAL_PATH/prompts/" "${VPS_ALIAS}:${VPS_PATH}/prompts/"
  echo -e "${GREEN}✓ Prompts synced${NC}"
else
  echo -e "${RED}⚠ Warning: prompts/ directory not found locally${NC}"
fi

# Step 3: Sync .env file
echo -e "${YELLOW}[3/4] Syncing environment configuration...${NC}"
if [ -f "$LOCAL_PATH/.env" ]; then
  rsync -avz \
    "$LOCAL_PATH/.env" "${VPS_ALIAS}:${VPS_PATH}/.env"
  echo -e "${GREEN}✓ Environment configuration synced${NC}"
else
  echo -e "${RED}⚠ Warning: .env file not found locally${NC}"
fi

# Step 4: Set up Python environment on VPS
echo -e "${YELLOW}[4/4] Setting up Python environment on VPS...${NC}"
ssh "${VPS_ALIAS}" << 'ENDSSH'
cd /root/Sisters-On-WhatsApp

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Python environment ready"
ENDSSH

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. SSH to VPS: ssh xserver-vps"
echo "2. Test the bot: cd /root/Sisters-On-WhatsApp && source venv/bin/activate"
echo "3. Run: python -m uvicorn src.whatsapp_webhook.server:app --host 0.0.0.0 --port 8001"
echo ""
echo -e "${YELLOW}To set up systemd service:${NC}"
echo "./scripts/setup_systemd.sh"
