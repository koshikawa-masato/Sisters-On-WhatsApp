# Conversation Learning System

**Status**: ✅ Deployed and Active

## Overview

The conversation learning system allows the three sisters to learn from user corrections and build a verified knowledge base. This creates a feedback loop where hallucinations can be corrected and remembered.

## How It Works

### 1. Automatic Correction Detection

When users provide corrections in conversations, the system automatically detects them:

**English Patterns**:
- "Actually, it's called [name]"
- "No, it's called [name]"
- "It's called [name]"
- "The correct name is [name]"

**Chinese Patterns**:
- "其實是 [名字]"
- "應該是 [名字]"
- "叫做 [名字]"
- "那家店叫 [名字]"

### 2. Fact Storage

Detected corrections are automatically stored in `prompts/pending_facts.json`:

```json
{
  "pending": [
    {
      "fact": "心斎橋焙煎所",
      "category": "place",
      "confidence": 0.8,
      "source": {
        "phone_number": "+1234567890",
        "message": "其實是心斎橋焙煎所",
        "context": "assistant: 聽說大阪心齋橋有間時尚咖啡廳\nuser: 那家店叫什麼名字呢？",
        "timestamp": "2025-11-24T11:43:42.131061"
      },
      "status": "pending",
      "verification": null
    }
  ]
}
```

### 3. Grok Verification

Use Grok (X.AI) to verify pending facts using real-time X (Twitter) data:

**Manual Verification**:
```bash
# Check a specific fact
python scripts/grok_factcheck.py --check "心斎橋焙煎所"

# Output example:
# ======================================================================
# Verified: True
# Confidence: 95%
# Evidence: Found multiple X posts mentioning 心斎橋焙煎所 as a specialty
#           coffee roastery in Shinsaibashi, Osaka. Known for latte art.
# Sources: X post 1, X post 2, Google Maps
# ======================================================================
```

**Auto-Verification (Recommended)**:
```bash
# Check all pending facts
python scripts/grok_factcheck.py --auto

# This will:
# 1. Query all pending facts from prompts/pending_facts.json
# 2. Verify each fact using Grok API
# 3. Move verified facts (confidence >= 70%) to verified_knowledge.json
# 4. Move rejected facts to rejected list
```

**Search Knowledge Base**:
```bash
# Search for specific facts
python scripts/grok_factcheck.py --search "心斎橋"

# List all verified facts
python scripts/grok_factcheck.py --list
```

### 4. Verified Knowledge Injection

When a user asks about a topic, the system:

1. Searches `prompts/verified_knowledge.json` for relevant facts
2. If matches found, injects verified knowledge into system prompt:

```
## VERIFIED KNOWLEDGE (from past conversations)

**心斎橋焙煎所** (places):
  - Location: Shinsaibashi, Osaka
  - Type: Coffee roastery & cafe
  - Known for: Specialty coffee, latte art
  - Confidence: 95%
```

3. Sister responds confidently with correct information

### 5. Complete Learning Loop Example

**Initial Conversation** (Hallucination):
```
User: 聽說大阪心齋橋有間時尚咖啡廳。那家店叫什麼名字呢？
Botan: Hmm, maybe "LINK"? Not totally sure but that name rings a bell! 😊
```

**User Provides Correction**:
```
User: 其實是心斎橋焙煎所
System: ✅ User correction detected: 心斎橋焙煎所 (confidence: 80%)
         → Stored in prompts/pending_facts.json
```

**Verification** (Manual or Cron):
```bash
$ python scripts/grok_factcheck.py --auto
🔍 Verifying pending facts...
✅ Verified: 心斎橋焙煎所 (confidence: 95%)
   → Moved to prompts/verified_knowledge.json
```

**Next Conversation** (Learned):
```
User: 大阪心齋橋有什麼好的咖啡廳？
Botan: Oh! 心斎橋焙煎所 is a really nice specialty coffee place in
       Shinsaibashi! They're known for their amazing latte art and
       fresh-roasted beans. ☕✨
```

## Configuration

Add to `.env`:

```bash
# Grok API (for fact-checking)
GROK_API_KEY=your_grok_api_key_here
GROK_MODEL=grok-2-1212
GROK_API_URL=https://api.x.ai/v1/chat/completions
GROK_TEMPERATURE=0.1
GROK_MAX_TOKENS=1000

# Fact-checking confidence threshold (0.0-1.0)
FACTCHECK_CONFIDENCE_THRESHOLD=0.7
```

## Cron Job Setup (Recommended)

Automate daily fact verification:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 23:00 every day)
0 23 * * * cd /root/Sisters-On-WhatsApp && source venv/bin/activate && python scripts/grok_factcheck.py --auto >> /var/log/sisters-whatsapp/factcheck.log 2>&1
```

## Files

- **`src/memory/conversation_learner.py`**: Detects corrections and manages pending facts
- **`scripts/grok_factcheck.py`**: Grok-powered fact verification system
- **`prompts/pending_facts.json`**: Unverified facts from user corrections (gitignored)
- **`prompts/verified_knowledge.json`**: Verified facts for sisters' memory (gitignored)
- **`src/characters/personality.py`**: Injects verified knowledge into prompts

## Testing

Run integration tests:

```bash
# Test correction detection, learning, and knowledge injection
python test_learning_loop.py

# Expected output:
# ✅ PASS: Correction Detection
# ✅ PASS: Conversation Learning
# ✅ PASS: Verified Knowledge Injection
# ✅ PASS: Complete Workflow
```

## Monitoring

**Check Pending Facts**:
```bash
cat prompts/pending_facts.json | jq '.pending | length'
```

**Check Verified Knowledge**:
```bash
cat prompts/verified_knowledge.json | jq '.places | length'
```

**View Logs**:
```bash
# On VPS
ssh production-server 'journalctl -u sisters-whatsapp -f | grep "correction"'
```

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONVERSATION LEARNING LOOP                   │
└─────────────────────────────────────────────────────────────────┘

1️⃣ User provides correction
   "其實是心斎橋焙煎所"
         ↓
2️⃣ CorrectionDetector extracts fact
   Pattern: "其實是 [fact]"
   Extracted: "心斎橋焙煎所"
         ↓
3️⃣ Store in pending_facts.json
   Status: pending
   Confidence: 0.8
         ↓
4️⃣ Grok verification (manual/cron)
   $ python scripts/grok_factcheck.py --auto
   Searches X (Twitter) for evidence
         ↓
5️⃣ If confidence >= 70%
   Move to verified_knowledge.json
         ↓
6️⃣ Next conversation
   User mentions "心斎橋" → Inject verified knowledge
         ↓
7️⃣ Sister responds confidently
   "Oh! 心斎橋焙煎所 is a really nice specialty coffee place..."

✅ Learning complete!
```

## Benefits

1. **No More Repeated Mistakes**: Once corrected, sisters remember
2. **User-Driven Knowledge**: Learning from real user corrections
3. **Verification**: Grok ensures accuracy before adding to memory
4. **Transparent**: Users see sisters learn and improve
5. **Scalable**: Knowledge base grows naturally over time

## Cost

- **Grok API**: ~$5-15/month (with daily cron job)
- **Storage**: Negligible (JSON files in `prompts/`)

## Future Enhancements

- [ ] Web dashboard for reviewing pending facts
- [ ] Multi-source verification (Grok + web search)
- [ ] User reputation system (trust frequent correctors more)
- [ ] Knowledge sharing between sisters (verified by one, used by all)
- [ ] Analytics: "Most corrected topics", "Learning rate"

---

**Last Updated**: 2025-11-24
**Status**: Production-ready and deployed
