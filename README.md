# Sisters-On-WhatsApp

**Multi-personality AI chatbot for WhatsApp with automatic character selection**

## Overview

Sisters-On-WhatsApp is an AI chatbot featuring three distinct AI personalities (sisters) who automatically respond based on conversation topics. Built for WhatsApp Business API and targeting global English-speaking markets.

## The Three Sisters

- **Botan** 🌸 - Social media enthusiast and entertainment expert
  - Topics: Streaming, content creation, pop culture, social media
  - Personality: Friendly, energetic, outgoing

- **Kasho** 🎵 - Music professional and life advisor
  - Topics: Music production, instruments, career advice, relationships
  - Personality: Professional, thoughtful, supportive

- **Yuri** 📚 - Book lover and creative thinker
  - Topics: Literature, creative writing, science fiction, philosophy
  - Personality: Thoughtful, inquisitive, literary

## Key Features

- ✨ **Automatic Character Selection** - System intelligently routes questions to the appropriate sister based on topic
- 🌐 **Global Accessibility** - Built on WhatsApp platform, accessible worldwide
- 🎭 **Distinct Personalities** - Each sister has unique expertise, speech patterns, and personality traits
- 💬 **Natural Conversations** - Context-aware responses with conversation memory
- 🚀 **Scalable Architecture** - FastAPI backend with PostgreSQL session management

## Technical Stack

- **Platform**: WhatsApp Business API (Cloud API)
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **LLM**: Kimi (moonshot-v1-8k) - Long context, cost-effective
- **Backup LLMs**: OpenAI GPT-4o-mini, Claude Haiku, Gemini Flash
- **Hosting**: VPS (production deployment)

## Project Status

✅ **Alpha Testing** - WhatsApp bot is live and functional!

## Try It Now

**Test the Three Sisters on WhatsApp:**

[![Chat on WhatsApp](https://img.shields.io/badge/Chat%20on-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/14155238886?text=join%20situation-completely)

**How to start:**
1. Click the button above or send a WhatsApp message to: **+1 (415) 523-8886**
2. Send the join code: `join situation-completely`
3. Start chatting! Try asking:
   - "Who knows a lot about streaming?" → **Botan** 🌸 will respond
   - "Can you help me with music production?" → **Kasho** 🎵 will respond
   - "What's a good sci-fi book?" → **Yuri** 📚 will respond

**Note**: This is a Twilio Sandbox for testing. The bot automatically selects which sister responds based on your topic!

## Documentation

- [Design Specification](docs/design/Sisters_On_WhatsApp_Design_Specification.md) - Comprehensive design document
- [Character Guide](docs/Character_Guide.md) - Detailed character profiles and personality traits
- [API Integration](docs/API_Integration.md) - WhatsApp Business API integration guide

## Architecture

```
User (WhatsApp) → WhatsApp Business API → Webhook Server
                                             ↓
                                       Topic Analyzer
                                             ↓
                                      Character Router
                                             ↓
                              ┌──────────────┼──────────────┐
                              ↓              ↓              ↓
                           Botan         Kasho           Yuri
                              ↓              ↓              ↓
                              └──────────────┼──────────────┘
                                             ↓
                                      LLM Engine
                                             ↓
                                  WhatsApp Message Formatter
                                             ↓
                                   WhatsApp Business API
                                             ↓
                                     User (WhatsApp)
```

## Related Projects

- [AI-Vtuber-Project](https://github.com/koshikawa-masato/AI-Vtuber-Project) - Original LINE Bot implementation (Japanese + English)

## Inspiration

This project is inspired by Japanese VTuber culture, where AI personalities have distinct characteristics and fan bases. Sisters-On-WhatsApp adapts this concept for global markets, introducing character-driven AI interaction design to Western audiences.

## License

Private project - All rights reserved

## Author

**Koshikawa Masato** - 50 years of technology passion
- Working with Claude Code (Kuroko) in equal partnership
- Building innovative AI × Character × Messaging products

---

🤖 **Generated with Claude Code (Kuroko)**

Co-Authored-By: Claude <noreply@anthropic.com>
