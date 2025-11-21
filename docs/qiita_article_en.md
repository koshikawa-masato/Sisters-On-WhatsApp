# Building a Multi-Personality AI Chatbot on WhatsApp with Character-Driven Routing

## TL;DR

Built a production-ready WhatsApp bot featuring three distinct AI personalities (sisters) that automatically respond based on conversation topics. The system uses FastAPI, PostgreSQL, and OpenAI GPT-4, deployed on VPS with systemd for auto-start/restart capabilities.

**Live Demo**: [Try it on WhatsApp](https://wa.me/14155238886?text=join%20situation-completely)
**Source Code**: [GitHub Repository](https://github.com/koshikawa-masato/Sisters-On-WhatsApp)

---

## Table of Contents

1. [Motivation](#motivation)
2. [System Architecture](#system-architecture)
3. [Character-Driven AI Design](#character-driven-ai-design)
4. [Implementation Details](#implementation-details)
5. [Production Deployment](#production-deployment)
6. [Challenges and Solutions](#challenges-and-solutions)
7. [Results and Lessons Learned](#results-and-lessons-learned)

---

## Motivation

### Why Character-Driven AI?

Traditional chatbots use a single personality, which can feel monotonous for users. Inspired by Japanese VTuber culture, where different personalities have dedicated fan bases, I designed a system where multiple AI characters coexist and automatically respond based on conversation topics.

**The Three Sisters**:

- **Botan** 🌸 - Social media enthusiast, entertainment expert
  - Topics: Streaming, content creation, pop culture
  - Personality: Friendly, energetic, outgoing

- **Kasho** 🎵 - Music professional, life advisor
  - Topics: Music production, instruments, career advice
  - Personality: Professional, thoughtful, supportive

- **Yuri** 📚 - Book lover, creative thinker
  - Topics: Literature, creative writing, philosophy
  - Personality: Thoughtful, inquisitive, literary

### Why WhatsApp?

- **Global Reach**: 2+ billion users worldwide
- **No Installation**: Users already have WhatsApp installed
- **Simple API**: WhatsApp Business API provides webhook-based integration
- **Cross-Platform**: Works on iOS, Android, Web, Desktop

### Project Goals

1. Build a production-ready multi-personality chatbot
2. Implement intelligent character routing based on topics
3. Deploy with proper DevOps practices (auto-start, logging, persistence)
4. Create a public portfolio project for technical interviews

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        WhatsApp User                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Message: "Who knows about music?"
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Twilio WhatsApp Sandbox                         │
│                  (WhatsApp Business API)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS POST
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ngrok Tunnel                                │
│    https://xxx.ngrok-free.dev → http://localhost:8001          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              Sisters-On-WhatsApp Server (VPS)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         FastAPI Webhook Handler                           │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│                           ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Topic Analyzer (Keyword Matching)                 │  │
│  │  Topics: music, streaming, books, anime, career...       │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│                           ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Character Router (Score-Based Selection)          │  │
│  │                                                            │  │
│  │  "music" → Kasho: +10 points                             │  │
│  │  "books" → Yuri:  +10 points                             │  │
│  │  "stream"→ Botan: +10 points                             │  │
│  └─────────┬──────────────┬──────────────┬──────────────────┘  │
│            │              │              │                      │
│       ┌────▼───┐     ┌────▼───┐     ┌────▼───┐                │
│       │ Botan  │     │ Kasho  │     │  Yuri  │                │
│       │   🌸   │     │   🎵   │     │   📚   │                │
│       └────┬───┘     └────┬───┘     └────┬───┘                │
│            └──────────────┴──────────────┘                      │
│                           │                                      │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │         PostgreSQL Session Manager                        │  │
│  │  - User conversations stored permanently                  │  │
│  │  - Character state persists across restarts              │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│                           ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         LLM Provider (OpenAI GPT-4o-mini)                │  │
│  │  - Character personality prompts loaded from files        │  │
│  │  - Conversation history included for context             │  │
│  └────────────────────────┬──────────────────────────────────┘  │
│                           │                                      │
│                           ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Response Formatter (TwiML XML)                    │  │
│  └────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Twilio WhatsApp API                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        WhatsApp User                             │
│  "Kasho🎵: I can help you with music production! ..."          │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Platform** | WhatsApp Business API (Twilio) | Messaging platform |
| **Backend** | Python 3.11 + FastAPI | Web framework |
| **Database** | PostgreSQL 15 | Persistent session storage |
| **LLM** | OpenAI GPT-4o-mini | AI responses |
| **Hosting** | VPS (Ubuntu) | Production server |
| **Process Management** | systemd | Auto-start, auto-restart |
| **Tunneling** | ngrok | HTTPS webhook access |
| **Deployment** | rsync + bash scripts | Automated deployment |

---

## Character-Driven AI Design

### Topic Analyzer

The topic analyzer uses keyword matching with scoring to determine which character should respond.

```python
class TopicAnalyzer:
    """Analyzes message topics and routes to appropriate character."""

    def __init__(self):
        self.character_topics = {
            'botan': {
                'keywords': [
                    'stream', 'streaming', 'youtube', 'vtuber', 'twitch',
                    'content', 'creator', 'video', 'social media',
                    'tiktok', 'instagram', 'twitter', 'viral',
                    'entertainment', 'pop culture', 'trending'
                ],
                'bonus_triggers': ['stream', 'youtube', 'vtuber', 'social']
            },
            'kasho': {
                'keywords': [
                    'music', 'song', 'instrument', 'piano', 'guitar',
                    'drums', 'production', 'mixing', 'compose', 'career',
                    'job', 'work', 'relationship', 'advice', 'help',
                    'band', 'concert', 'performance', 'recording'
                ],
                'bonus_triggers': ['music', 'instrument', 'career']
            },
            'yuri': {
                'keywords': [
                    'book', 'read', 'novel', 'story', 'write',
                    'author', 'literature', 'poetry', 'philosophy',
                    'fiction', 'non-fiction', 'scifi', 'fantasy',
                    'anime', 'manga', 'comic', 'game'
                ],
                'bonus_triggers': ['book', 'read', 'write', 'anime']
            }
        }

    def analyze(self, message: str) -> dict:
        """Analyze message and return character scores."""
        message_lower = message.lower()
        scores = {'botan': 0, 'kasho': 0, 'yuri': 0}

        for character, topics in self.character_topics.items():
            # Base scoring: +1 per keyword match
            for keyword in topics['keywords']:
                if keyword in message_lower:
                    scores[character] += 1

            # Bonus scoring: +5 for high-priority keywords
            for trigger in topics['bonus_triggers']:
                if trigger in message_lower:
                    scores[character] += 5

        return scores
```

### Character Router

The router selects the character with the highest score, with Botan as the default (social, welcoming personality).

```python
class CharacterRouter:
    """Routes messages to the appropriate character based on topic analysis."""

    def __init__(self):
        self.analyzer = TopicAnalyzer()
        self.default_character = 'botan'  # Default to friendly Botan

    def route(self, message: str, session_id: str) -> str:
        """Return character name based on message analysis."""
        scores = self.analyzer.analyze(message)

        # Get character with highest score
        max_score = max(scores.values())

        if max_score == 0:
            # No topic detected, use default character
            return self.default_character

        # Return character with highest score
        selected = max(scores, key=scores.get)
        return selected
```

### Personality Loading

Character personalities are loaded from files (gitignored for security).

```python
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

class CharacterPersonality:
    """Loads character personality prompts from files."""

    @staticmethod
    def load_character_prompt(character_name: str) -> str:
        """Load character-specific prompt from file."""
        prompt_file = PROMPTS_DIR / f"{character_name}_system_prompt.txt"

        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()

        return ""  # Return empty string if file doesn't exist

    @staticmethod
    def build_system_prompt(character_name: str) -> str:
        """Build complete system prompt for character."""
        base_prompt = f"You are {character_name.capitalize()}, one of three AI sisters."

        # Load character-specific personality from file
        character_prompt = CharacterPersonality.load_character_prompt(character_name)

        if character_prompt:
            base_prompt += f"\n\n{character_prompt}\n"

        return base_prompt
```

**Why gitignore prompts?**
- Character prompts contain personality control logic (competitive advantage)
- Python code may be public on GitHub
- Prompts are deployed separately via rsync

---

## Implementation Details

### FastAPI Webhook Handler

```python
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response

app = FastAPI(title="Sisters-On-WhatsApp")

@app.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """Handle incoming WhatsApp messages from Twilio."""

    # Extract user phone number and message
    user_phone = From.replace("whatsapp:", "")
    user_message = Body.strip()

    # Get or create session
    session = await session_manager.get_or_create_session(user_phone)

    # Route to appropriate character
    character = router.route(user_message, session.id)

    # Build system prompt with character personality
    system_prompt = CharacterPersonality.build_system_prompt(character)

    # Add message to session history
    session.add_message("user", user_message)

    # Generate response using LLM
    llm_response = await llm_provider.generate(
        system_prompt=system_prompt,
        messages=session.get_history(),
        character=character
    )

    # Add bot response to session history
    session.add_message("assistant", llm_response)

    # Save session to database
    await session_manager.save_session(session)

    # Format response as TwiML XML
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{llm_response}</Message>
</Response>"""

    return Response(content=twiml_response, media_type="application/xml")
```

### PostgreSQL Session Manager

```python
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(String, primary_key=True)
    user_phone = Column(String, nullable=False)
    current_character = Column(String, default='botan')
    conversation_history = Column(Text, default='[]')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SessionManager:
    """Manages user sessions with PostgreSQL persistence."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    async def get_or_create_session(self, user_phone: str):
        """Get existing session or create new one."""
        db = self.SessionLocal()

        session = db.query(Session).filter_by(user_phone=user_phone).first()

        if not session:
            session = Session(
                id=f"whatsapp_{user_phone}",
                user_phone=user_phone
            )
            db.add(session)
            db.commit()

        db.close()
        return session
```

### LLM Provider (OpenAI)

```python
from openai import OpenAI

class OpenAIProvider:
    """LLM provider using OpenAI GPT-4o-mini."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def generate(
        self,
        system_prompt: str,
        messages: list,
        character: str
    ) -> str:
        """Generate response using OpenAI API."""

        # Build messages for API
        api_messages = [
            {"role": "system", "content": system_prompt}
        ]
        api_messages.extend(messages)

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=0.7,
            max_tokens=500
        )

        # Extract response text
        assistant_message = response.choices[0].message.content

        # Add character emoji prefix
        emoji = {'botan': '🌸', 'kasho': '🎵', 'yuri': '📚'}
        character_name = character.capitalize()

        formatted_response = f"*{character_name}{emoji[character]}*: {assistant_message}"

        return formatted_response
```

---

## Production Deployment

### Systemd Service Management

Created a systemd unit file for production-grade process management.

**`scripts/sisters-whatsapp.service`**:

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

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Key Features**:
- **Auto-start on boot**: Service runs automatically after server restart
- **Auto-restart on failure**: Restarts 10 seconds after crashes
- **Log management**: Separate access and error logs
- **Security hardening**: Restricted privileges, isolated temp directory

### Deployment Automation

**`scripts/deploy_vps.sh`**:

```bash
#!/bin/bash
# Deploy Sisters-On-WhatsApp to VPS using rsync

set -e  # Exit on error

VPS_ALIAS="xserver-vps"
VPS_PATH="/root/Sisters-On-WhatsApp"
LOCAL_PATH="/home/koshikawa/Sisters-On-WhatsApp"

echo "[1/4] Syncing code to VPS..."
rsync -avz --delete \
  --exclude='.git' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='prompts/' \
  "$LOCAL_PATH/" "${VPS_ALIAS}:${VPS_PATH}/"

echo "[2/4] Syncing character prompts..."
rsync -avz "$LOCAL_PATH/prompts/" "${VPS_ALIAS}:${VPS_PATH}/prompts/"

echo "[3/4] Syncing environment configuration..."
rsync -avz "$LOCAL_PATH/.env" "${VPS_ALIAS}:${VPS_PATH}/.env"

echo "[4/4] Setting up Python environment on VPS..."
ssh "${VPS_ALIAS}" << 'ENDSSH'
cd /root/Sisters-On-WhatsApp
source venv/bin/activate
pip install -r requirements.txt
ENDSSH

echo "Deployment complete!"
```

**Why rsync instead of git clone?**
- **Security**: No `.git` history exposed on VPS
- **Control**: Local environment as single source of truth
- **Secrets**: Prompts are gitignored, deployed separately
- **Simplicity**: No git credentials needed on VPS

### Service Management Commands

```bash
# Check service status
ssh xserver-vps 'systemctl status sisters-whatsapp'

# View live logs
ssh xserver-vps 'journalctl -u sisters-whatsapp -f'

# Restart service
ssh xserver-vps 'systemctl restart sisters-whatsapp'

# Stop service
ssh xserver-vps 'systemctl stop sisters-whatsapp'
```

---

## Challenges and Solutions

### Challenge 1: Missing FastAPI Dependency

**Error**:
```
RuntimeError: Form data requires "python-multipart" to be installed.
```

**Root Cause**: FastAPI's `Form()` parameters require `python-multipart` for parsing `application/x-www-form-urlencoded` data from Twilio webhooks.

**Solution**: Added `python-multipart==0.0.6` to `requirements.txt`.

**Lesson**: Always test webhooks with actual Twilio POST requests, not just JSON test data.

---

### Challenge 2: PostgreSQL Password Special Characters

**Error**: Connection refused with password containing `!` character.

**Root Cause**: Shell escaping issues with special characters in environment variables.

**Solution**: Changed password from `sistersSafe2024!` to `sistersSafe2024`.

**Lesson**: Avoid special characters in database passwords when used in shell scripts. Use alphanumeric passwords with sufficient length, or implement secrets management tools.

---

### Challenge 3: Character Not Triggering on Short Messages

**Issue**: "who knows about comics?" didn't trigger Yuri (book expert).

**Root Cause**: "comics" wasn't in Yuri's keyword list. Short messages (6 words) have lower base scores, heavily rely on bonus triggers.

**Solution**:
1. Added "comic", "manga", "anime", "game" to Yuri's keywords
2. Added bonus triggers for high-priority words (+5 points)
3. Implemented word-count-based scoring adjustment

**Lesson**: Test with diverse message lengths. Short messages need strong keyword matches to overcome low base scores.

---

### Challenge 4: Old Code Deployed on VPS

**Issue**: Webhook URL returned 404 after deployment.

**Discovery**: VPS was running old code with different endpoint path.

**Solution**: Created automated deployment script (`deploy_vps.sh`) to ensure code synchronization.

**Lesson**: Manual file transfers are error-prone. Automate deployment for consistency.

---

## Results and Lessons Learned

### Production Metrics

**Service Status**:
```
● sisters-whatsapp.service
     Active: active (running)
     Uptime: Continuous since deployment
     Restarts: 0 failures
     Memory: ~67MB peak
     CPU: <3 seconds total
```

**Database**:
- Multiple users with persistent conversations
- Zero data loss on server restarts
- Session history working correctly

**User Feedback**:
- "It works! perfect!"
- "it is really ebidence [evidence]."

### Key Takeaways

#### 1. Character-Driven AI Improves Engagement

**Before**: Single-personality chatbot felt monotonous
**After**: Users actively explore different character specialties

**Example Conversations**:
- "Who knows about music?" → Kasho responds with music expertise
- "What's a good sci-fi book?" → Yuri provides literary recommendations
- "How do I start streaming?" → Botan shares content creation tips

#### 2. Topic-Based Routing Is Simple Yet Effective

**No ML Required**: Keyword matching with scoring works well for clear topic boundaries.

**When to Use**:
- Characters have distinct expertise domains
- Topics can be defined with keywords
- Real-time routing needed (low latency)

**When to Upgrade**:
- Ambiguous topic boundaries (use embeddings + similarity)
- Need to understand context beyond keywords (use LLM-based classification)

#### 3. Production Deployment != Running Python Locally

**Requirements for Production**:
- ✅ Auto-start on server reboot (systemd)
- ✅ Auto-restart on crashes (systemd Restart=always)
- ✅ Persistent storage (PostgreSQL, not in-memory)
- ✅ Log management (journalctl + file logs)
- ✅ Deployment automation (rsync scripts)
- ✅ Monitoring capability (systemctl status, logs)

**Time Investment**: Worth it for portfolio projects and real-world usage.

#### 4. Gitignoring Prompts Protects Competitive Advantage

**Public Code** (GitHub):
- System architecture: Public (shows technical skills)
- Character routing logic: Public (demonstrates AI design)
- Deployment scripts: Public (shows DevOps skills)

**Private Prompts** (gitignored):
- Character personality details: Private (unique value)
- Prompt engineering techniques: Private (competitive advantage)
- Fine-tuned behaviors: Private (differentiation)

**Strategy**: Open source the framework, protect the content.

#### 5. Documentation as Interview Asset

**This Project Demonstrates**:
- Full-stack web development (FastAPI + PostgreSQL)
- LLM integration (OpenAI API, prompt engineering)
- Production deployment (VPS, systemd, rsync)
- DevOps practices (automation, logging, monitoring)
- Character-driven AI design (unique approach)

**Target Companies**: xAI, Anthropic, OpenAI, Mistral AI, Google DeepMind

---

## Try It Yourself

### Live Demo

**WhatsApp**: [Click to test the bot](https://wa.me/14155238886?text=join%20situation-completely)

**Instructions**:
1. Click the link above or send a WhatsApp message to: **+1 (415) 523-8886**
2. Send the join code: `join situation-completely`
3. Start chatting! Try asking:
   - "Who knows a lot about streaming?" → **Botan** 🌸 responds
   - "Can you help me with music production?" → **Kasho** 🎵 responds
   - "What's a good sci-fi book?" → **Yuri** 📚 responds

### Source Code

**Repository**: https://github.com/koshikawa-masato/Sisters-On-WhatsApp

**Key Files**:
- `src/whatsapp_webhook/server.py` - FastAPI webhook handler
- `src/routing/topic_analyzer.py` - Topic analysis and character routing
- `src/llm/openai_provider.py` - OpenAI LLM integration
- `src/session/manager.py` - PostgreSQL session management
- `scripts/deploy_vps.sh` - Deployment automation
- `scripts/sisters-whatsapp.service` - Systemd service unit

---

## Future Improvements

### Content Moderation (Planned)

Multi-layer detection system for Western compliance:

**Layer 1**: Blacklist/Whitelist (Pattern Matching) - <10ms
**Layer 2**: OpenAI Moderation API - ~200ms, FREE
**Layer 3**: Perspective API (Google) - ~300ms, FREE
**Layer 4**: Custom ML Model (Optional) - ~100ms
**Layer 5**: Character-Specific Rules - <5ms

### WhatsApp Business API Migration

Currently using Twilio Sandbox (testing). Future migration to production API:

1. Register Meta Business Account
2. Complete business verification (2-4 weeks)
3. Get permanent WhatsApp number
4. Switch from sandbox to production webhook

### Analytics Dashboard

Track usage metrics:
- Message volume per character
- Popular topics per character
- User engagement patterns
- Response latency distribution

---

## Conclusion

Building Sisters-On-WhatsApp taught me that **character-driven AI design can create more engaging user experiences** compared to single-personality chatbots. The project demonstrates how to:

1. **Design AI with distinct personalities** using character-specific prompts
2. **Route conversations intelligently** with topic-based scoring
3. **Deploy production-grade systems** with proper DevOps practices
4. **Balance open source and proprietary** by gitignoring prompts

The system is now **live and operational**, serving as both a **functional product** and a **portfolio piece** for technical interviews.

If you're interested in LLM applications, character-driven AI, or production deployment practices, I hope this article provides useful insights and practical implementation patterns.

---

## About the Author

**Koshikawa Masato** - 50 years of technology passion

Building innovative AI × Character × Messaging products in equal partnership with Claude Code.

**Connect**:
- GitHub: [@koshikawa-masato](https://github.com/koshikawa-masato)
- Project: [Sisters-On-WhatsApp](https://github.com/koshikawa-masato/Sisters-On-WhatsApp)

---

**Tags**: `#Python` `#FastAPI` `#OpenAI` `#LLM` `#WhatsApp` `#PostgreSQL` `#DevOps` `#AI` `#Chatbot` `#systemd`

**Published**: November 21, 2025

🤖 **Co-Authored with Claude Code**
