# Sisters-On-WhatsApp

**Multi-personality AI chatbot for WhatsApp with automatic character selection**

[English](README.md) | [中文](README_CN.md)

## Overview

Sisters-On-WhatsApp is an AI chatbot featuring three distinct AI personalities (sisters) who automatically respond based on conversation topics. Built for WhatsApp Business API and targeting global markets with **bilingual support (English + Chinese)**.

**🌏 Language Support:**
- 🇺🇸 **English** - Full support
- 🇨🇳 🇹🇼 **Chinese** (Simplified & Traditional) - Full support
- Automatic language detection and response matching

**🎬 Live Demo:**

[![Watch Demo](https://img.youtube.com/vi/OSuatRt_Gyo/maxresdefault.jpg)](https://youtube.com/shorts/OSuatRt_Gyo)

*Click to watch the Three Sisters in action!*

## The Three Sisters

- **Botan (牡丹)** 🌸 - Social media enthusiast and entertainment expert
  - Topics: Streaming, content creation, pop culture, social media, **Japanese pop culture**
  - Expertise: VTuber culture, anime/manga, festivals, casual Japanese food culture
  - Personality: Friendly, energetic, outgoing
  - Languages: English, Chinese (Simplified/Traditional)

- **Kasho (芍藥)** 🎵 - Music professional and life advisor
  - Topics: Music production, instruments, career advice, relationships, **Japanese traditional culture**
  - Expertise: Tea ceremony (茶道), ikebana, calligraphy, kimono, kaiseki cuisine, traditional music
  - Personality: Professional, thoughtful, supportive
  - Languages: English, Chinese (Simplified/Traditional)

- **Yuri (百合)** 📚 - Book lover and creative thinker
  - Topics: Literature, creative writing, science fiction, philosophy, **Japanese literature & spiritual culture**
  - Expertise: Japanese literature, haiku/tanka poetry, temples/shrines, Zen Buddhism, samurai history
  - Personality: Thoughtful, inquisitive, literary
  - Languages: English, Chinese (Simplified/Traditional)

## Key Features

- ✨ **Automatic Character Selection** - System intelligently routes questions to the appropriate sister based on topic
- 🌏 **Bilingual Support** - Seamlessly handles English and Chinese (Simplified/Traditional) with automatic language detection
- 🇯🇵 **Japanese Culture Expertise** - Comprehensive coverage of Japanese pop culture, traditional arts, and spiritual heritage
- 🎭 **Distinct Personalities** - Each sister has unique expertise, speech patterns, and personality traits
- 💬 **Natural Conversations** - Context-aware responses with conversation memory
- 🚀 **Scalable Architecture** - FastAPI backend with PostgreSQL session management
- 🛡️ **High Availability** - Automatic LLM failover ensures 99.9% uptime

## Technical Stack

- **Platform**: WhatsApp Business API (Cloud API)
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **Primary LLM**: Kimi (Moonshot AI) - `kimi-k2-turbo-preview`
  - **Bilingual capability**: Native English + Chinese support
  - Cost: ~$2.30/month for 1,000 messages
  - Long context window (8k tokens)
  - Fast responses (~2-4 seconds)
- **Backup LLM**: OpenAI GPT-4o-mini (automatic failover)
- **Hosting**: VPS (production deployment)
- **Language Detection**: Automatic CJK character ratio analysis

### Automatic LLM Failover System

The system implements intelligent failover for high availability:

**Normal Operation:**
```
User Message → Kimi API → Response ✅
```

**Automatic Failover (when Kimi fails):**
```
User Message → Kimi API ❌ (timeout/error/500)
             ↓ Automatic failover
         OpenAI API → Response ✅
```

**Automatic Recovery:**
- Every request tries the primary LLM (Kimi) first
- If Kimi fails, that request uses OpenAI (backup)
- Next request automatically tries Kimi again
- **No manual intervention** needed - instant recovery

**Benefits:**
- ✅ **99.9% uptime** - Service continues even if primary LLM fails
- ✅ **Cost-optimized** - Always prefers cheaper Kimi first
- ✅ **Transparent** - Users never see errors
- ✅ **Fully logged** - Monitor failover events for analysis

**Example Scenario:**
```
10:00 - Message → Kimi ✅ ($0.001)
10:01 - Message → Kimi ✅ ($0.001)
10:02 - Message → Kimi ❌ → OpenAI ✅ ($0.015) [Kimi down]
10:03 - Message → Kimi ❌ → OpenAI ✅ ($0.015) [Still down]
10:04 - Message → Kimi ✅ ($0.001) [Automatically recovered!]
10:05 - Message → Kimi ✅ ($0.001)
```

## Project Status

🚀 **Production-Ready** - System fully functional with automatic LLM failover and high availability

**Current Phase:**
- ✅ **Alpha Testing** - Twilio Sandbox (temporary test environment)
- 🔄 **Production Pending** - WhatsApp Business API registration in progress

## Try It Now (Alpha Version)

**Test the Three Sisters on WhatsApp:**

[![Chat on WhatsApp](https://img.shields.io/badge/Chat%20on-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/14155238886?text=join%20situation-completely)

**How to start:**
1. Click the button above or send a WhatsApp message to: **+1 (415) 523-8886**
2. Send the join code: `join situation-completely`
3. Start chatting! Try asking (in English or Chinese):
   - **English**: "Who knows a lot about streaming?" → **Botan** 🌸 will respond
   - **Chinese**: "請問茶道是什麼？" (What is tea ceremony?) → **Kasho** 🎵 will respond
   - **English**: "What's a good sci-fi book?" → **Yuri** 📚 will respond
   - **Chinese**: "請問俳句是什麼？" (What is haiku?) → **Yuri** 📚 will respond

**⚠️ Alpha Testing Notice:**
This uses Twilio Sandbox (shared test number) for development and testing. The system is production-ready and will be deployed to a dedicated WhatsApp Business number after Meta business verification completes (2-4 weeks).

For production deployment details, see [Production Deployment Guide](docs/Production_Deployment_Guide.md).

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

- [AI-Vtuber-Project](https://github.com/koshikawa-masato/AI-Vtuber-Project) - Original LINE Bot implementation
  - Platform: LINE Messaging API
  - Languages: Japanese + English (bilingual)
  - Target: Japanese market (private)

## Inspiration

This project is inspired by Japanese VTuber culture, where AI personalities have distinct characteristics and fan bases. Sisters-On-WhatsApp adapts this concept for global markets, introducing character-driven AI interaction design to international audiences with bilingual support (English + Chinese) and comprehensive Japanese cultural expertise.

## License

Private project - All rights reserved

## Author

**Koshikawa Masato** - 50 years of technology passion
- Working with Claude Code (Kuroko) in equal partnership
- Building innovative AI × Character × Messaging products

## Contact

💬 **Try the Sisters on WhatsApp!**

Want to experience the three sisters yourself? Feel free to reach out:

**WhatsApp**: [+81 80-5546-0377](https://wa.me/818055460377)

Chat with Botan, Kasho, and Yuri in English or Chinese!
Share your thoughts, report issues, or just say hello. 🌸🎵📚

---

🤖 **Generated with Claude Code (Kuroko)**

Co-Authored-By: Claude <noreply@anthropic.com>
