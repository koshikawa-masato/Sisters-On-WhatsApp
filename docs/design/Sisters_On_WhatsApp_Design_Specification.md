# Sisters-On-WhatsApp - Design Specification

**Project Name**: Sisters-On-WhatsApp (SoW)
**Alternative Names**: WhatsApp Sisters, Three Sisters Global Edition
**Version**: 1.0
**Date**: 2025-11-21
**Author**: Koshikawa Masato + Claude Code (Kuroko)
**Status**: Design Phase

---

## 1. Executive Summary

**Sisters-On-WhatsApp (SoW)** is an international adaptation of the Botan Project's Three Sisters AI chatbot, optimized for WhatsApp's platform constraints and targeting global English-speaking markets.

**Key Innovation**: Multi-personality AI chatbot with automatic character selection based on conversation topics, accessible through WhatsApp's global platform.

**Target Markets**: USA, Europe, English-speaking Asia (India, Singapore, Philippines)

---

## 2. Project Goals

### Primary Goals
1. **Platform Adaptation**: Port the Three Sisters concept from LINE to WhatsApp
2. **Language Focus**: English-only implementation for global accessibility
3. **Simplification**: Auto mode only (no manual character selection)
4. **Market Validation**: Test Western market receptiveness to character-driven AI

### Secondary Goals
1. **Interview Asset**: Demonstrable project for xAI, Anthropic, OpenAI, Mistral interviews
2. **Cross-Platform Learning**: Understand WhatsApp Business API constraints
3. **Cultural Bridge**: Introduce VTuber-inspired AI personality design to Western markets
4. **Technical Portfolio**: Show adaptability across messaging platforms

---

## 3. Platform Comparison

### LINE Bot (Current Implementation)

**Advantages**:
- ✅ Rich Menus with custom images
- ✅ Flex Messages for complex layouts
- ✅ Free tier for developers
- ✅ Push messages anytime
- ✅ Stickers and character expressions
- ✅ Quick setup (hours)

**Limitations**:
- ❌ Primarily Asia market
- ❌ Not widely known in Western tech circles
- ❌ Requires explaining LINE to Western audiences

### WhatsApp Business API (Target Platform)

**Advantages**:
- ✅ Global reach (2+ billion users)
- ✅ Well-known in Western markets
- ✅ Professional image for business applications
- ✅ End-to-end encryption
- ✅ Familiar to interview panels

**Limitations**:
- ❌ Costs per conversation (~$0.005-0.09)
- ❌ Business verification required (2-4 weeks)
- ❌ 24-hour conversation window restriction
- ❌ Message templates need Meta approval
- ❌ No rich menus or complex UI elements
- ❌ Limited interactive features

---

## 4. System Architecture

### High-Level Architecture

```
User (WhatsApp)
    ↓ (Message)
WhatsApp Business API
    ↓ (Webhook)
FastAPI Webhook Server (VPS)
    ↓
Topic Analyzer
    ↓
Character Router
    ├─→ Botan (Entertainment, VTuber, Social Media)
    ├─→ Kasho (Music, Audio, Professional)
    └─→ Yuri (Literature, Anime, Subculture)
    ↓
Character LLM Engine
    ↓ (Response)
WhatsApp Message Formatter
    ↓
WhatsApp Business API
    ↓ (Delivery)
User (WhatsApp)
```

### Component Breakdown

#### 1. WhatsApp Business API Interface
- **Technology**: Meta Cloud API or On-Premises API
- **Authentication**: Access token + Phone Number ID
- **Webhook**: HTTPS endpoint for incoming messages
- **Message Types**: Text, image, audio, document, location

#### 2. Topic Analyzer
- **Current Implementation**: Simple keyword matching + pattern database
- **Upgrade Option**: GPT-4o-mini for topic classification (~$0.0001/message)
- **Topics**: Entertainment, Music, Literature, General

#### 3. Character Router
- **Input**: Topic classification result
- **Output**: Selected character (Botan, Kasho, or Yuri)
- **Fallback**: Botan handles general topics

#### 4. Character LLM Engine
- **Options**: OpenAI GPT-4o-mini, Claude Haiku, or Gemini Flash
- **Character Prompts**: Adapted from LINE version
- **Language**: English only
- **Context**: Session history (30 messages)

#### 5. Session Manager
- **Storage**: PostgreSQL (existing infrastructure)
- **Data**: user_id, character_history, topic_history, last_message_at
- **Language field**: Removed (English only)

---

## 5. Simplifications from LINE Version

### Removed Features
1. ❌ **Rich Menus** - WhatsApp doesn't support them
2. ❌ **Manual Character Selection** - Auto mode only
3. ❌ **Language Switching** - English only
4. ❌ **Flex Messages** - Text and simple buttons only
5. ❌ **Character Stickers** - Not available on WhatsApp
6. ❌ **Bilingual System Prompts** - Simplified to English

### Retained Core Features
1. ✅ **Three Character Personalities** - Botan, Kasho, Yuri
2. ✅ **Topic-Based Routing** - Intelligent character selection
3. ✅ **Character Backstories** - Adapted for international audience
4. ✅ **Conversation Memory** - PostgreSQL session management
5. ✅ **Trend Integration** - Daily trends from Grok (optional)
6. ✅ **Multi-LLM Support** - OpenAI, Claude, Gemini

---

## 6. Character Adaptations for Global Audience

### Botan (牡丹)
**Original**: LA-returnee, Japanese gyaru, VTuber fan
**Adapted**: Social media enthusiast, entertainment expert, friendly and outgoing
**Topics**: Social media, streaming, content creation, pop culture
**Speech Pattern**: Casual, energetic, uses emojis

### Kasho (花相)
**Original**: Eldest sister, music professional, Japanese instruments
**Adapted**: Music professional, audio engineer, responsible advisor
**Topics**: Music production, instruments, career advice, relationships
**Speech Pattern**: Professional, thoughtful, supportive

### Yuri (百合)
**Original**: Youngest sister, light novel reader, Japanese subculture
**Adapted**: Book lover, creative writer, curious learner
**Topics**: Books, creative writing, science fiction, philosophy
**Speech Pattern**: Thoughtful, inquisitive, literary references

---

## 7. User Experience Flow

### First Conversation
```
User: "Hi there!"

Botan: "Hey! 👋 I'm Botan, one of the Three Sisters!
We're an AI chatbot team - I handle entertainment stuff,
my sister Kasho knows all about music, and Yuri is our
book nerd. What brings you here today?"
```

### Topic-Based Switching
```
User: "Can you recommend some good sci-fi books?"

[System: Topic = Literature → Route to Yuri]

Yuri: "Oh, a fellow sci-fi reader! 📚 I'm Yuri, by the way.
Let me suggest some favorites..."
```

### Continuity
```
User: "Wait, who are you now?"

Yuri: "I'm Yuri, the youngest of the Three Sisters! Botan
talked to you earlier - we automatically switch based on
topics. Think of us as a team of specialists. Is this confusing?
I can explain more!"
```

---

## 8. Technical Implementation

### Phase 1: Setup (Week 1-2)
- [ ] Register WhatsApp Business account
- [ ] Complete Meta Business verification
- [ ] Set up Cloud API or On-Premises API
- [ ] Configure webhook endpoint on VPS
- [ ] Test message sending/receiving

### Phase 2: Core Development (Week 3-4)
- [ ] Adapt webhook_server_vps.py for WhatsApp
- [ ] Implement WhatsApp message parser
- [ ] Create WhatsApp message formatter
- [ ] Port character prompts to English
- [ ] Adapt topic analyzer for English input
- [ ] Test with development phone number

### Phase 3: Character Tuning (Week 5-6)
- [ ] Test Botan personality (entertainment topics)
- [ ] Test Kasho personality (music topics)
- [ ] Test Yuri personality (literature topics)
- [ ] Refine character switching logic
- [ ] Adjust topic classification accuracy
- [ ] Add explanation system ("Why did the character change?")

### Phase 4: Beta Testing (Week 7-8)
- [ ] Invite 5-10 test users
- [ ] Collect feedback on character personalities
- [ ] Monitor topic routing accuracy
- [ ] Measure conversation quality
- [ ] Calculate cost per conversation
- [ ] Optimize for WhatsApp's 24-hour window

---

## 9. Cost Analysis

### WhatsApp Business API Costs
- **Authentication conversations**: $0.0050/conversation (24h window)
- **Marketing conversations**: $0.0150/conversation
- **Service conversations**: $0.0100/conversation
- **Utility conversations**: $0.0050/conversation

**Estimated Monthly Cost** (100 active users, 10 messages/user/month):
- Messages: 1,000 total
- Conversations: ~200 (grouped within 24h windows)
- Cost: $1-3/month

### LLM API Costs
- **GPT-4o-mini**: $0.00015/1K input, $0.0006/1K output
- **Claude Haiku**: $0.00025/1K input, $0.00125/1K output
- **Gemini Flash**: $0.000075/1K input, $0.0003/1K output

**Estimated Monthly Cost** (1,000 messages):
- Average: 500 input + 200 output tokens per message
- GPT-4o-mini: ~$0.20/month
- **Total: $1-5/month for small scale**

---

## 10. Success Metrics

### Technical Metrics
- [ ] Message delivery rate > 99%
- [ ] Average response time < 3 seconds
- [ ] Topic classification accuracy > 85%
- [ ] Character consistency score (user feedback)

### User Engagement Metrics
- [ ] Active users (weekly active users)
- [ ] Messages per user per week
- [ ] Conversation retention (users returning after 7 days)
- [ ] Character preference distribution

### Business Metrics
- [ ] Cost per conversation < $0.05
- [ ] User satisfaction score (survey)
- [ ] Interview mention rate (how often it impresses interviewers)

---

## 11. Risks and Mitigations

### Risk 1: Meta Approval Delays
**Impact**: High
**Likelihood**: Medium
**Mitigation**: Start verification process early, have backup demo plan for interviews

### Risk 2: User Confusion (Character Switching)
**Impact**: Medium
**Likelihood**: High
**Mitigation**: Add clear intro message, "Why did the character change?" explainer

### Risk 3: Cost Overrun
**Impact**: Low
**Likelihood**: Low
**Mitigation**: Set monthly budget cap in WhatsApp settings, monitor usage daily

### Risk 4: Cultural Translation Issues
**Impact**: Medium
**Likelihood**: Medium
**Mitigation**: Beta test with native English speakers, adjust character backstories

---

## 12. Interview Positioning

### Elevator Pitch (30 seconds)
> "I built Sisters-On-WhatsApp, a multi-personality AI chatbot where three AI characters with distinct expertise respond based on conversation topics. It's inspired by Japanese VTuber culture but adapted for global markets. The system automatically routes entertainment questions to Botan, music questions to Kasho, and literature questions to Yuri. I built it on WhatsApp to make it accessible to Western audiences."

### Technical Deep-Dive (5 minutes)
1. **Architecture**: FastAPI webhook → Topic analyzer → Character router → LLM engine
2. **Innovation**: Character-driven AI vs. generic assistant approach
3. **Challenge**: Adapting from LINE (rich UI) to WhatsApp (text-focused)
4. **Learning**: Cross-platform messaging APIs, character consistency, topic classification
5. **Cultural Bridge**: Bringing Japanese AI personality design to Western markets

### Demo Strategy
- Share WhatsApp number with interviewer
- Send sample messages showing character switching
- Explain topic routing logic
- Show GitHub repo with architecture diagrams

---

## 13. Future Enhancements

### Version 2.0 (Post-Launch)
- [ ] Voice message support (each sister has unique voice)
- [ ] Image analysis (multimodal input)
- [ ] Group chat support (all three sisters in one chat)
- [ ] User memory system (remember past conversations)
- [ ] Emotion detection and response

### Version 3.0 (Advanced)
- [ ] Custom character creation (users define their own "sister")
- [ ] Multi-language support (Spanish, French, Hindi)
- [ ] Integration with external APIs (Spotify, Goodreads)
- [ ] Analytics dashboard for users
- [ ] Premium tier with advanced features

---

## 14. Open Questions

1. **Character names in English**: Keep "Botan, Kasho, Yuri" or use English names?
   - **Recommendation**: Keep Japanese names + English nicknames ("Botan (Bo)")

2. **VTuber culture explanation**: How much to explain in intro message?
   - **Recommendation**: Brief mention, let users discover naturally

3. **Fallback behavior**: What if topic is ambiguous?
   - **Recommendation**: Default to Botan (most versatile character)

4. **Character consistency**: Should same user always get same sister for same topic?
   - **Recommendation**: Yes, maintain consistency within session

5. **Pricing model**: Free tier + premium, or completely free?
   - **Recommendation**: Start completely free for portfolio/interview purposes

---

## 15. Next Steps

### Immediate (This Week)
1. [ ] Review and approve this design specification
2. [ ] Register WhatsApp Business account
3. [ ] Start Meta business verification process
4. [ ] Create project repository structure

### Short-term (Weeks 2-4)
1. [ ] Set up WhatsApp Cloud API
2. [ ] Implement basic webhook handler
3. [ ] Port character prompts to English
4. [ ] Test with development number

### Medium-term (Weeks 5-8)
1. [ ] Complete character personality tuning
2. [ ] Beta test with 5-10 users
3. [ ] Prepare demo for interviews
4. [ ] Document learnings and challenges

---

## 16. Appendix

### A. Technology Stack
- **Messaging Platform**: WhatsApp Business API (Cloud or On-Premises)
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **LLM**: OpenAI GPT-4o-mini (primary), Claude Haiku (backup)
- **Hosting**: XServer VPS (existing infrastructure)
- **Monitoring**: Simple logging to PostgreSQL

### B. Repository Structure
```
Sisters-On-WhatsApp/
├── src/
│   ├── whatsapp_webhook/
│   │   ├── webhook_server.py
│   │   ├── message_parser.py
│   │   ├── message_formatter.py
│   │   └── session_manager.py
│   ├── characters/
│   │   ├── botan.py
│   │   ├── kasho.py
│   │   └── yuri.py
│   ├── routing/
│   │   ├── topic_analyzer.py
│   │   └── character_router.py
│   └── llm/
│       └── llm_provider.py
├── prompts/
│   ├── botan_system_prompt.txt
│   ├── kasho_system_prompt.txt
│   └── yuri_system_prompt.txt
├── docs/
│   ├── API_Integration.md
│   ├── Character_Guide.md
│   └── Deployment.md
├── scripts/
│   ├── setup_whatsapp.sh
│   └── deploy_vps.sh
└── README.md
```

### C. Related Documents
- Original LINE Bot: `/home/koshikawa/AI-Vtuber-Project/`
- Character Profiles: `/home/koshikawa/kirinuki/2025-11-11/三姉妹プロフィール_LINE Bot用.md`
- Architecture Document: `docs/03_architecture/vps/LINE_Bot_Bilingual_Mode_Architecture.md`

---

**Status**: Design specification approved - Ready for implementation
**Next Review**: After Phase 1 completion (WhatsApp API setup)

---

🤖 **Generated with Claude Code (Kuroko)**

Co-Authored-By: Claude <noreply@anthropic.com>
