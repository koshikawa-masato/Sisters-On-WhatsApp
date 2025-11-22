# Production Deployment Guide

**Sisters-On-WhatsApp - Production Deployment Specification**

> **Version**: 1.0
> **Last Updated**: 2025-11-22
> **Status**: Production-Ready System

---

## Table of Contents

1. [Overview](#overview)
2. [Current Status (Sandbox)](#current-status-sandbox)
3. [Production Requirements](#production-requirements)
4. [WhatsApp Business API Setup](#whatsapp-business-api-setup)
5. [VPS Deployment](#vps-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Cost Analysis](#cost-analysis)

---

## Overview

This guide covers the complete production deployment process for Sisters-On-WhatsApp, from WhatsApp Business API registration to VPS deployment and ongoing maintenance.

**Deployment Timeline**: 4-6 weeks (due to Meta business verification)

---

## Current Status (Sandbox)

### Twilio Sandbox Configuration

**Current Setup (Testing Only):**
- **Phone Number**: +1 (415) 523-8886 (shared)
- **Join Code**: `join situation-completely`
- **Webhook**: VPS endpoint at http://162.43.4.11:8001/whatsapp
- **Status**: ✅ Fully functional for testing

**Limitations:**
- ❌ Users must send join code first
- ❌ Shared number with other developers
- ❌ Sessions expire after 3 days of inactivity
- ❌ Cannot customize sender name/profile
- ❌ Not suitable for real users
- ⚠️ **Production use NOT recommended**

---

## Production Requirements

### 1. Business Entity

**Required:**
- ✅ Registered business (sole proprietorship acceptable)
- ✅ Business name
- ✅ Business address
- ✅ Business phone number
- ✅ Business email
- ✅ Business website (optional but recommended)

**For Personal Projects:**
- Can register as sole proprietor
- Use personal name as business name
- Home address acceptable
- Personal phone/email acceptable

### 2. Meta Business Account

**Requirements:**
- Facebook Business Manager account
- Business verification documents
- Payment method (credit card)
- Phone number for verification

### 3. Technical Requirements

**Infrastructure:**
- ✅ VPS with public IP (already have: 162.43.4.11)
- ✅ Domain name with SSL (optional: can use IP + Cloudflare Tunnel)
- ✅ PostgreSQL database (already configured)
- ✅ Python 3.11+ environment (already set up)

**Current VPS:**
- Provider: XServer VPS
- IP: 162.43.4.11
- User: root
- Project: /root/Sisters-On-WhatsApp
- Status: ✅ Production-ready

---

## WhatsApp Business API Setup

### Option 1: Twilio WhatsApp Business API (Recommended)

**Why Twilio:**
- ✅ Easier setup (already using Twilio)
- ✅ Better documentation
- ✅ Reliable infrastructure
- ✅ Good for MVP and demos
- ✅ Interview-friendly (professional setup)

#### Step 1: Meta Business Verification (2-4 weeks)

1. **Create Meta Business Account**
   - Go to: https://business.facebook.com
   - Click "Create Account"
   - Enter business details

2. **Complete Business Verification**
   - Upload business documents:
     - Business registration (if company)
     - OR government-issued ID (if sole proprietor)
     - Proof of address (utility bill, bank statement)
   - Wait for verification: **2-4 weeks**
   - Status emails sent to business email

3. **Verification Tips**
   - Use clear, high-quality scans
   - Ensure all documents match business name
   - Respond quickly to verification requests
   - **Timeline**: 2-4 weeks (can be faster)

#### Step 2: Twilio WhatsApp Sender Setup (1 day)

1. **Enable WhatsApp in Twilio Console**
   - Login: https://console.twilio.com
   - Navigate to: Messaging → Try it out → Send a WhatsApp message
   - Click "Enable WhatsApp"

2. **Request WhatsApp Sender**
   - Go to: Messaging → Senders → WhatsApp senders
   - Click "Request to add Sender"
   - Enter business details (must match Meta verification)
   - Submit for approval

3. **Purchase Phone Number**
   - Navigate to: Phone Numbers → Buy a number
   - Select country (USA recommended: +1)
   - Filter: SMS + Voice capabilities
   - Purchase number (~$1-2/month)

4. **Link Number to WhatsApp**
   - In WhatsApp senders, select purchased number
   - Complete SMS verification
   - Submit to Meta for approval
   - **Approval time**: 1-3 business days

#### Step 3: Configure Webhook

1. **Update Webhook URL in Twilio**
   ```
   Webhook URL: https://your-domain.com/whatsapp
   OR: http://162.43.4.11:8001/whatsapp (if using IP)
   ```

2. **Set HTTP Method**: POST

3. **Update .env on VPS**
   ```bash
   # Update these values:
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1XXXXXXXXXX  # Your new number
   WEBHOOK_VERIFY_TOKEN=your_secure_token_here
   ```

4. **Test Webhook**
   - Send message to your WhatsApp number
   - Check logs: `tail -f /var/log/sisters-whatsapp/error.log`
   - Verify response received

#### Step 4: Submit Message Templates (1 week)

WhatsApp requires pre-approved templates for proactive messages.

**Template Types:**
1. **Welcome Message** (when user first contacts)
2. **Error/Fallback Message**
3. **Session Timeout Notification** (optional)

**Example Welcome Template:**
```
Name: sisters_welcome
Category: UTILITY
Language: English

Body:
Hello! 👋 Welcome to Sisters-On-WhatsApp!

We're three AI sisters who can help you with different topics:

🌸 *Botan* - Social media & entertainment
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

Just ask your question, and the right sister will respond!
```

**Submit Templates:**
1. Twilio Console → Messaging → Content Editor
2. Create new template
3. Wait for Meta approval: 1-3 business days

---

### Option 2: Meta WhatsApp Cloud API (Direct)

**Why Direct:**
- ✅ No middleman fees
- ✅ Free tier (1,000 conversations/month)
- ✅ Full control

**Why NOT (for this project):**
- ❌ More complex setup
- ❌ Need to handle webhooks/infrastructure
- ❌ Less documentation
- ❌ Not as interview-friendly

**Setup Steps** (if choosing this option):
1. Meta Business verification (same as above)
2. Register app at https://developers.facebook.com
3. Enable WhatsApp Cloud API
4. Configure webhook endpoint
5. Get production access (separate approval)
6. Link phone number

**Not recommended for Sisters-On-WhatsApp** - Twilio is simpler and better for MVP.

---

## VPS Deployment

### Current Production Setup

**VPS Information:**
- **Provider**: XServer VPS
- **IP**: 162.43.4.11
- **SSH**: `ssh xserver-vps` (configured)
- **User**: root
- **Password**: cha1me2983
- **Project Path**: /root/Sisters-On-WhatsApp

**Services Running:**
- **Application**: sisters-whatsapp.service (systemd)
- **Database**: PostgreSQL 15
- **Port**: 8001 (HTTP)
- **Logs**: /var/log/sisters-whatsapp/

### Deployment Process

#### 1. Code Deployment (via rsync)

**Why rsync (not git clone):**
- ✅ Security: Doesn't expose .git history
- ✅ Control: Deploy only necessary files
- ✅ Secrets: Prompts directory deployed separately
- ✅ Simplicity: No git credentials needed on VPS

**Deploy Script** (create if needed):
```bash
#!/bin/bash
# scripts/deploy_vps.sh

echo "🚀 Deploying Sisters-On-WhatsApp to VPS..."

# Sync code
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
  /home/koshikawa/Sisters-On-WhatsApp/src/ \
  xserver-vps:/root/Sisters-On-WhatsApp/src/

# Sync prompts (gitignored)
rsync -avz \
  /home/koshikawa/Sisters-On-WhatsApp/prompts/ \
  xserver-vps:/root/Sisters-On-WhatsApp/prompts/

# Restart service
ssh xserver-vps 'systemctl restart sisters-whatsapp'

echo "✅ Deployment complete!"
```

#### 2. Systemd Service (already configured)

**Service File**: `/etc/systemd/system/sisters-whatsapp.service`

```ini
[Unit]
Description=Sisters-On-WhatsApp Bot (WhatsApp Business API)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/Sisters-On-WhatsApp
Environment="PATH=/root/Sisters-On-WhatsApp/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/root/Sisters-On-WhatsApp/.env
ExecStart=/root/Sisters-On-WhatsApp/venv/bin/python -m uvicorn src.whatsapp_webhook.server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=append:/var/log/sisters-whatsapp/access.log
StandardError=append:/var/log/sisters-whatsapp/error.log

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Service Commands:**
```bash
# Start service
systemctl start sisters-whatsapp

# Stop service
systemctl stop sisters-whatsapp

# Restart service
systemctl restart sisters-whatsapp

# Check status
systemctl status sisters-whatsapp

# View logs
journalctl -u sisters-whatsapp -f

# Enable auto-start on boot
systemctl enable sisters-whatsapp
```

#### 3. SSL/HTTPS Setup (Optional but Recommended)

**Current**: Using HTTP on port 8001 (IP: 162.43.4.11)

**For Production**: Use HTTPS with domain or Cloudflare Tunnel

**Option A: Cloudflare Tunnel** (Recommended - Free)
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# Login and create tunnel
cloudflared tunnel login
cloudflared tunnel create sisters-whatsapp
cloudflared tunnel route dns sisters-whatsapp whatsapp.yourdomain.com

# Run tunnel
cloudflared tunnel run sisters-whatsapp
```

**Option B: Nginx + Let's Encrypt**
```nginx
server {
    listen 80;
    server_name whatsapp.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name whatsapp.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/whatsapp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/whatsapp.yourdomain.com/privkey.pem;

    location /whatsapp {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Environment Configuration

### Production .env File

**Location**: `/root/Sisters-On-WhatsApp/.env`

```bash
# Twilio (Production - Update after WhatsApp sender approval)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+1XXXXXXXXXX  # Your production number
WEBHOOK_VERIFY_TOKEN=your_secure_random_token_here

# LLM Configuration
PRIMARY_LLM=kimi
KIMI_API_KEY=sk-your-kimi-api-key
KIMI_MODEL=kimi-k2-turbo-preview
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Other LLM APIs (optional)
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=xai-your-key
GROK_MODEL=grok-4-fast

# Database (PostgreSQL on VPS)
POSTGRES_HOST=162.43.4.11
POSTGRES_PORT=5432
POSTGRES_DB=sisters_on_whatsapp
POSTGRES_USER=sisters
POSTGRES_PASSWORD=your_secure_password_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
ENVIRONMENT=production

# LLM Generation Settings
LLM_TEMPERATURE=0.8
LLM_MAX_TOKENS=500

# Content Moderation
MODERATION_STRICT_MODE=true
```

**Security Checklist:**
- ✅ Use strong passwords (20+ characters)
- ✅ Never commit .env to git (already gitignored)
- ✅ Rotate API keys quarterly
- ✅ Use different tokens for dev/prod
- ✅ Enable 2FA on all service accounts

---

## Monitoring & Maintenance

### Health Monitoring

#### 1. Application Health Check

**Endpoint**: http://162.43.4.11:8001/health

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "llm": "Kimi (kimi-k2-turbo-preview)",
    "characters": ["botan", "kasho", "yuri"],
    "database": "connected"
  }
}
```

**Monitoring Script**:
```bash
#!/bin/bash
# scripts/check_health.sh

HEALTH_URL="http://162.43.4.11:8001/health"
RESPONSE=$(curl -s $HEALTH_URL)

if echo $RESPONSE | grep -q '"status":"healthy"'; then
  echo "✅ Service is healthy"
  exit 0
else
  echo "❌ Service is unhealthy!"
  echo $RESPONSE
  exit 1
fi
```

**Cron Job** (check every 5 minutes):
```bash
*/5 * * * * /root/Sisters-On-WhatsApp/scripts/check_health.sh
```

#### 2. Log Monitoring

**Application Logs**:
```bash
# Error log
tail -f /var/log/sisters-whatsapp/error.log

# Access log
tail -f /var/log/sisters-whatsapp/access.log

# Systemd logs
journalctl -u sisters-whatsapp -f
```

**Watch for:**
- ⚠️ LLM failover events (Kimi → OpenAI)
- ❌ 401/403 errors (API key issues)
- ⚠️ Database connection errors
- ❌ Content moderation blocks

#### 3. Performance Metrics

**Monitor:**
- Response time (should be <5 seconds)
- LLM API latency (Kimi: ~2-4s, OpenAI: ~1-3s)
- Database query time
- Memory usage
- CPU usage

**Commands**:
```bash
# Service resource usage
systemctl status sisters-whatsapp

# Memory usage
free -h

# Disk usage
df -h

# Process info
ps aux | grep uvicorn
```

### Automatic Failover Monitoring

**Check Failover Logs**:
```bash
# Look for failover events
grep "Primary LLM.*failed" /var/log/sisters-whatsapp/error.log

# Count failovers today
grep "Primary LLM.*failed" /var/log/sisters-whatsapp/error.log | grep "$(date +%Y-%m-%d)" | wc -l

# Check if OpenAI was used
grep "Failover successful.*openai" /var/log/sisters-whatsapp/error.log
```

**Alert if:**
- More than 10 failovers per hour → Kimi API issues
- More than 50 failovers per day → Consider switching primary
- Both LLMs failing → Critical incident

### Database Maintenance

**Backup Schedule**:
```bash
# Daily backup script
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="/root/backups/sisters-whatsapp"
DATE=$(date +%Y%m%d-%H%M%S)
PGPASSWORD="your_password" pg_dump -h 162.43.4.11 -U sisters -d sisters_on_whatsapp \
  > $BACKUP_DIR/backup-$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup-*.sql" -mtime +7 -delete
```

**Cron**:
```bash
0 2 * * * /root/Sisters-On-WhatsApp/scripts/backup_db.sh
```

### Update Procedure

**Safe Update Process**:
```bash
# 1. Test locally first
# (on local machine)
cd /home/koshikawa/Sisters-On-WhatsApp
pytest tests/

# 2. Backup database
ssh xserver-vps '/root/Sisters-On-WhatsApp/scripts/backup_db.sh'

# 3. Deploy code
./scripts/deploy_vps.sh

# 4. Restart service
ssh xserver-vps 'systemctl restart sisters-whatsapp'

# 5. Check health
curl http://162.43.4.11:8001/health

# 6. Monitor logs for 5 minutes
ssh xserver-vps 'tail -f /var/log/sisters-whatsapp/error.log'
```

---

## Cost Analysis

### Monthly Operating Costs

#### WhatsApp Business API (Twilio)

**Conversation Pricing**:
- Marketing: ~$0.027 per conversation
- Utility: ~$0.005 per conversation
- Authentication: ~$0.005 per conversation
- Service: ~$0.009 per conversation

**Sisters-On-WhatsApp** (Utility category):
- First 1,000 conversations: **FREE**
- After 1,000: ~$0.005 each

**Example Usage**:
- 100 users × 10 messages/month = 1,000 conversations
- **Cost**: $0/month (within free tier)
- 500 users × 10 messages/month = 5,000 conversations
- **Cost**: (5,000 - 1,000) × $0.005 = **$20/month**

#### LLM Costs

**Kimi (Primary)**:
- Cost: ~$2.30/month for 1,000 messages
- Current usage: <$1 for 2 days
- **Projected**: $15-30/month with heavy usage

**OpenAI (Backup/Failover)**:
- Only used when Kimi fails
- Estimated: <10% of requests
- **Projected**: $3-5/month

**Total LLM**: ~$18-35/month

#### Infrastructure

**VPS (XServer)**:
- Current plan: (check your XServer billing)
- Estimated: $10-30/month

**Database (PostgreSQL)**:
- Included in VPS (self-hosted)
- **Cost**: $0/month

#### Total Monthly Cost Estimate

**Low Usage** (100 users):
- WhatsApp: $0 (free tier)
- LLM: $18/month
- VPS: $10-30/month
- **Total**: ~$28-48/month

**Medium Usage** (500 users):
- WhatsApp: $20/month
- LLM: $25/month
- VPS: $10-30/month
- **Total**: ~$55-75/month

**High Usage** (2,000 users):
- WhatsApp: $50/month
- LLM: $35/month
- VPS: $30-50/month
- **Total**: ~$115-135/month

**Cost Optimization**:
- ✅ Kimi primary (10x cheaper than OpenAI)
- ✅ Automatic failover (reliability without extra cost)
- ✅ Free WhatsApp tier (first 1,000 conversations)
- ✅ Self-hosted database (no external DB costs)

---

## Production Checklist

### Pre-Launch

- [ ] Meta business verification completed
- [ ] WhatsApp sender approved by Meta
- [ ] Production phone number purchased
- [ ] Message templates approved
- [ ] SSL/HTTPS configured (Cloudflare or Nginx)
- [ ] .env production values set
- [ ] Database backups scheduled
- [ ] Health monitoring set up
- [ ] Error alerting configured

### Launch Day

- [ ] Code deployed to VPS
- [ ] Service running and healthy
- [ ] Webhook URL updated in Twilio
- [ ] Test message sent and received
- [ ] All three sisters responding correctly
- [ ] Character switching working
- [ ] Database persisting conversations
- [ ] LLM failover tested
- [ ] Logs being written correctly

### Post-Launch

- [ ] Monitor logs for 24 hours
- [ ] Check failover events
- [ ] Verify cost tracking
- [ ] User feedback collected
- [ ] Performance metrics reviewed
- [ ] Backup verified

---

## Troubleshooting

### Common Issues

#### 1. "Number not registered with WhatsApp Business"
- **Cause**: WhatsApp sender not approved yet
- **Solution**: Wait for Meta approval (1-3 business days)
- **Workaround**: Continue using sandbox for testing

#### 2. "Template not found"
- **Cause**: Message templates not approved
- **Solution**: Check template status in Twilio Console
- **Workaround**: Use free-form responses only

#### 3. "Webhook timeout"
- **Cause**: LLM taking too long to respond
- **Solution**: Check LLM failover logs
- **Check**: `grep "Primary LLM.*failed" /var/log/sisters-whatsapp/error.log`

#### 4. "Database connection refused"
- **Cause**: PostgreSQL not running or wrong credentials
- **Solution**: Check PostgreSQL status and .env settings
- **Fix**: `systemctl status postgresql`

#### 5. "Service keeps restarting"
- **Cause**: Missing environment variables or code errors
- **Solution**: Check systemd logs
- **Debug**: `journalctl -u sisters-whatsapp -n 100`

---

## Support & Resources

### Official Documentation

- **Twilio WhatsApp**: https://www.twilio.com/docs/whatsapp
- **Meta Business**: https://business.facebook.com/business/help
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp
- **Kimi API**: https://platform.moonshot.cn/docs

### Project Resources

- **Repository**: /home/koshikawa/Sisters-On-WhatsApp
- **Design Spec**: docs/design/Sisters_On_WhatsApp_Design_Specification.md
- **CLAUDE.md**: Internal development guidelines (gitignored)

### Contact

For production deployment assistance:
- Check logs first: `/var/log/sisters-whatsapp/error.log`
- Review health endpoint: http://162.43.4.11:8001/health
- Check systemd status: `systemctl status sisters-whatsapp`

---

**Version**: 1.0
**Last Updated**: 2025-11-22
**Status**: Ready for Production Deployment

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
