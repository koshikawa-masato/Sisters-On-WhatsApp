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
- **LLM**: OpenAI GPT-4o-mini (primary)
- **Hosting**: VPS (production deployment)

## Project Status

🚧 **Design Phase** - See [Design Specification](docs/design/Sisters_On_WhatsApp_Design_Specification.md) for detailed planning

## Quick Start

Coming soon - WhatsApp Business API setup in progress

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
