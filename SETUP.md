# Sisters-On-WhatsApp - Setup Guide

Complete setup instructions for local development and testing.

---

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+** (for session management)
- **Twilio Account** (free sandbox for testing)
- **API Keys**: Kimi (Moonshot AI) and OpenAI

---

## Step 1: Clone Repository

```bash
cd /home/koshikawa/Sisters-On-WhatsApp
```

---

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Setup PostgreSQL Database

### Option A: Local PostgreSQL

```bash
# Install PostgreSQL (if not installed)
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE sisters_on_whatsapp;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sisters_on_whatsapp TO your_user;
\q
```

### Option B: Use Existing VPS Database

Update `.env` with VPS credentials (see Step 5).

---

## Step 5: Configure Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Twilio (WhatsApp Sandbox)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# LLM API Keys
KIMI_API_KEY=your_kimi_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
PRIMARY_LLM=kimi
KIMI_MODEL=moonshot-v1-8k

# Database
POSTGRES_HOST=localhost  # or VPS IP
POSTGRES_PORT=5432
POSTGRES_DB=sisters_on_whatsapp
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
```

### Getting API Keys

**Kimi (Moonshot AI)**:
1. Register at https://platform.moonshot.cn/
2. Get API key from dashboard
3. Add to `.env` as `KIMI_API_KEY`

**OpenAI** (required for content moderation):
1. Register at https://platform.openai.com/
2. Create API key
3. Add to `.env` as `OPENAI_API_KEY`

**Twilio**:
1. Sign up at https://www.twilio.com/try-twilio
2. Go to WhatsApp Sandbox: Console → Messaging → Try it out → Send a WhatsApp message
3. Get Account SID and Auth Token from dashboard
4. Add to `.env`

---

## Step 6: Verify Prompts Exist

Ensure character prompts are in `prompts/` directory:

```bash
ls -la prompts/
# Should see:
# - botan_system_prompt.txt
# - kasho_system_prompt.txt
# - yuri_system_prompt.txt
```

**IMPORTANT**: Prompts are gitignored. If deploying to VPS, use rsync (see deployment guide).

---

## Step 7: Test Database Connection

```bash
python -c "from src.session.manager import SessionManager; sm = SessionManager(); print('Database connected!')"
```

---

## Step 8: Start Server

```bash
# Development mode (with auto-reload)
uvicorn src.whatsapp_webhook.server:app --reload --port 8000

# Or run directly
python -m src.whatsapp_webhook.server
```

Server will start at `http://localhost:8000`

Test health check:
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

---

## Step 9: Expose Server with ngrok

Twilio needs a public URL to send webhooks.

### Install ngrok

```bash
# Download from https://ngrok.com/download
# Or using snap:
sudo snap install ngrok
```

### Start ngrok Tunnel

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

---

## Step 10: Configure Twilio Webhook

1. Go to Twilio Console: https://console.twilio.com/
2. Navigate to: Messaging → Try it out → Send a WhatsApp message
3. Click "Sandbox settings"
4. Under "When a message comes in", paste your ngrok URL + `/whatsapp`:
   ```
   https://abc123.ngrok.io/whatsapp
   ```
5. Set HTTP method to **POST**
6. Save

---

## Step 11: Test with WhatsApp

1. Open WhatsApp on your phone
2. Send message to Twilio sandbox number (shown in Twilio console)
3. First, send the join code (e.g., "join <your-code>")
4. Then send any message to test!

Example messages:
- "Hi!" → Should respond with Botan (default character)
- "What music do you recommend?" → Should switch to Kasho
- "Have you read any good books?" → Should switch to Yuri

---

## Troubleshooting

### Server won't start

**Error: Missing API keys**
```bash
# Check .env file has required keys
cat .env | grep API_KEY
```

**Error: Database connection failed**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check .env database credentials are correct
```

### Webhook not receiving messages

**Check ngrok is running**:
```bash
# Should see active tunnel
ngrok http 8000
```

**Check webhook URL in Twilio**:
- Must be HTTPS (ngrok provides this)
- Must end with `/whatsapp`
- Example: `https://abc123.ngrok.io/whatsapp`

**Check server logs**:
```bash
# Look for incoming requests
# Should see: "Received message from whatsapp:+1234567890: ..."
```

### Character not switching

**Check topic analyzer**:
- Server logs show topic scores: `Topic scores: {'botan': 0.5, 'kasho': 0.2, 'yuri': 0.1}`
- Threshold for switching is 0.3 (configurable in `.env` as `CHARACTER_SWITCH_THRESHOLD`)

### Content moderation blocking legitimate messages

**Adjust moderation settings**:
```bash
# In .env, set strict mode to false
MODERATION_STRICT_MODE=false
```

### Prompts not loading

**Error: Prompt file not found**
```bash
# Ensure prompts exist
ls -la prompts/*.txt

# Check file names match:
# - botan_system_prompt.txt
# - kasho_system_prompt.txt
# - yuri_system_prompt.txt
```

---

## Development Workflow

### 1. Make Code Changes

Edit files in `src/` directory.

### 2. Server Auto-Reloads

If using `--reload` flag, server automatically restarts on file changes.

### 3. Test via WhatsApp

Send messages to test changes immediately.

### 4. Check Logs

Server logs show:
- Incoming messages
- Topic analysis scores
- Character selections
- LLM responses
- Errors

### 5. Iterate

Repeat steps 1-4.

---

## Testing Different Characters

**Force Botan** (social media/entertainment):
- "What's trending on social media?"
- "Tell me about VTubers"
- "Recommend a movie to watch"

**Force Kasho** (music/advice):
- "What instrument should I learn?"
- "I need career advice"
- "Help me with a relationship problem"

**Force Yuri** (books/philosophy):
- "Recommend a science fiction book"
- "What's the meaning of life?"
- "Tell me about philosophy"

---

## Configuration Options

All settings in `.env` (see `src/config.py` for full list):

### Character Routing

```bash
# Threshold for character switching (0.0-1.0)
# Higher = less switching, more continuity
CHARACTER_SWITCH_THRESHOLD=0.3

# Conversation history to include (messages)
CONVERSATION_HISTORY_LIMIT=10
```

### LLM Generation

```bash
# Temperature (0.0-2.0)
# Higher = more creative, lower = more consistent
LLM_TEMPERATURE=0.8

# Max tokens per response
LLM_MAX_TOKENS=500
```

### Content Moderation

```bash
# Strict mode (true/false)
MODERATION_STRICT_MODE=true
```

### Custom Response Messages

```bash
# Message when content is blocked
MODERATION_BLOCKED_MESSAGE="I'm sorry, but I can't respond to that..."

# Message when error occurs
ERROR_MESSAGE="Oops! Something went wrong..."
```

---

## Next Steps

Once local testing works:

1. **Register WhatsApp Business API** (for production, without sandbox limitations)
2. **Deploy to VPS** (see deployment guide - TBD)
3. **Set up monitoring** (logs, error tracking)
4. **Scale database** (if needed for many users)

---

## Quick Reference

### Start Development Server
```bash
source venv/bin/activate
uvicorn src.whatsapp_webhook.server:app --reload --port 8000
```

### Start ngrok Tunnel
```bash
ngrok http 8000
```

### Check Logs
```bash
# Server logs show all activity in terminal
```

### Test Health
```bash
curl http://localhost:8000/health
```

### Reload Prompts (without restart)
```python
# In Python console:
from src.characters.personality import CharacterPersonality
cp = CharacterPersonality()
cp.reload_prompts()
```

---

**Status**: Ready for local testing! 🚀

**Next**: Configure Twilio webhook with ngrok URL and start chatting.
