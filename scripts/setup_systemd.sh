#!/bin/bash
# Set up systemd service for Sisters-On-WhatsApp on VPS
# Auto-start on boot, auto-restart on failure

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# VPS Configuration
VPS_ALIAS="xserver-vps"
VPS_PATH="/root/Sisters-On-WhatsApp"
SERVICE_FILE="sisters-whatsapp.service"
LOCAL_SERVICE_PATH="scripts/${SERVICE_FILE}"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Sisters-On-WhatsApp Systemd Setup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Step 1: Copy service file to VPS
echo -e "${YELLOW}[1/5] Copying systemd service file to VPS...${NC}"
rsync -avz "${LOCAL_SERVICE_PATH}" "${VPS_ALIAS}:${VPS_PATH}/scripts/"
echo -e "${GREEN}✓ Service file copied${NC}"

# Step 2: Install and configure service
echo -e "${YELLOW}[2/5] Installing systemd service...${NC}"
ssh "${VPS_ALIAS}" << 'ENDSSH'
set -e

# Create log directory
mkdir -p /var/log/sisters-whatsapp
chmod 755 /var/log/sisters-whatsapp

# Copy service file to systemd directory
cp /root/Sisters-On-WhatsApp/scripts/sisters-whatsapp.service /etc/systemd/system/

# Reload systemd daemon
systemctl daemon-reload

echo "✓ Systemd service installed"
ENDSSH
echo -e "${GREEN}✓ Service installed${NC}"

# Step 3: Enable service
echo -e "${YELLOW}[3/5] Enabling service (auto-start on boot)...${NC}"
ssh "${VPS_ALIAS}" "systemctl enable sisters-whatsapp.service"
echo -e "${GREEN}✓ Service enabled${NC}"

# Step 4: Start service
echo -e "${YELLOW}[4/5] Starting service...${NC}"
ssh "${VPS_ALIAS}" "systemctl start sisters-whatsapp.service"
sleep 3
echo -e "${GREEN}✓ Service started${NC}"

# Step 5: Check service status
echo -e "${YELLOW}[5/5] Checking service status...${NC}"
ssh "${VPS_ALIAS}" "systemctl status sisters-whatsapp.service --no-pager" || true

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${YELLOW}Service Management Commands:${NC}"
echo "  Check status:  ssh ${VPS_ALIAS} 'systemctl status sisters-whatsapp'"
echo "  View logs:     ssh ${VPS_ALIAS} 'journalctl -u sisters-whatsapp -f'"
echo "  Restart:       ssh ${VPS_ALIAS} 'systemctl restart sisters-whatsapp'"
echo "  Stop:          ssh ${VPS_ALIAS} 'systemctl stop sisters-whatsapp'"
echo ""
echo -e "${YELLOW}Log Files:${NC}"
echo "  Access log:    /var/log/sisters-whatsapp/access.log"
echo "  Error log:     /var/log/sisters-whatsapp/error.log"
echo ""
