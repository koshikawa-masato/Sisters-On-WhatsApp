# Content Moderation & Sensitivity System Specification

**Project**: Sisters-On-WhatsApp (SoW)
**Document Type**: Technical Specification
**Version**: 1.0
**Date**: 2025-11-21
**Author**: Koshikawa Masato + Claude Code (Kuroko)
**Status**: Design Phase

---

## 1. Executive Summary

This document specifies the Content Moderation & Sensitivity System for Sisters-On-WhatsApp, designed to comply with Western regulatory requirements (GDPR, AI Act, FTC guidelines) while maintaining the character-driven conversation experience.

**Primary Goals**:
1. Detect and filter harmful content before AI response generation
2. Comply with Western content moderation regulations
3. Respect cultural differences between Japanese and Western markets
4. Maintain transparency and user trust
5. Protect minors and vulnerable users

**Key Challenge**: Balance safety with natural conversation flow - avoid over-filtering that breaks character immersion.

---

## 2. Regulatory Requirements

### European Union (GDPR + AI Act)

**GDPR Requirements**:
- ✅ Data processing transparency
- ✅ User consent for data storage
- ✅ Right to explanation (why content was flagged)
- ✅ Data minimization (don't store more than necessary)

**EU AI Act Requirements** (High-Risk AI System):
- ✅ Risk management system
- ✅ Data governance and management practices
- ✅ Technical documentation
- ✅ Record-keeping (audit logs)
- ✅ Transparency and user information
- ✅ Human oversight
- ✅ Accuracy, robustness, cybersecurity

### United States (FTC + State Laws)

**FTC Guidelines**:
- ✅ Truth in advertising (AI must not deceive users)
- ✅ Consumer protection (prevent harmful outputs)
- ✅ Anti-discrimination (no biased content filtering)

**California CPRA**:
- ✅ Privacy rights for California residents
- ✅ Sensitive personal information protection
- ✅ Opt-out mechanisms

**COPPA** (Children's Online Privacy Protection Act):
- ✅ Age verification (if targeting users under 13)
- ✅ Parental consent requirements
- ✅ Data collection limitations for minors

### WhatsApp Business Policy

**WhatsApp Terms of Service**:
- ❌ No spam or unsolicited messages
- ❌ No illegal content
- ❌ No harassment or hate speech
- ❌ No misleading information
- ❌ No intellectual property violations

**Violations can result in**:
- Account suspension
- Permanent ban
- Legal liability

---

## 3. System Architecture

### High-Level Architecture

```
User Message (WhatsApp)
    ↓
Webhook Server
    ↓
Input Sanitization
    ↓
╔═══════════════════════════════════════════════╗
║     Content Moderation Pipeline (Multi-Layer) ║
╠═══════════════════════════════════════════════╣
║  Layer 1: Blacklist/Whitelist (Pattern Match) ║
║  Layer 2: OpenAI Moderation API               ║
║  Layer 3: Perspective API (Toxicity)          ║
║  Layer 4: Custom ML Model (Western Context)   ║
║  Layer 5: Character-Specific Rules            ║
╚═══════════════════════════════════════════════╝
    ↓
Decision Engine
    ├─→ SAFE → Continue to Character LLM
    ├─→ WARNING → Soft warning + Continue (with caution)
    ├─→ BLOCK → Reject + Send educational message
    └─→ REPORT → Block + Log for human review
    ↓
Audit Log (PostgreSQL)
```

### Component Breakdown

#### Layer 1: Blacklist/Whitelist (Pattern Matching)
- **Technology**: Regex + keyword lists
- **Speed**: <10ms
- **Purpose**: Quick filter for known bad patterns
- **Examples**:
  - Profanity lists
  - Explicit sexual terms
  - Hate speech keywords
  - URLs to known harmful sites

#### Layer 2: OpenAI Moderation API
- **Technology**: OpenAI's moderation endpoint
- **Speed**: ~200-500ms
- **Cost**: Free (included with OpenAI API)
- **Categories**:
  - Sexual content
  - Hate speech
  - Harassment
  - Self-harm
  - Violence
  - Illegal activities

#### Layer 3: Perspective API (Google)
- **Technology**: Google's Perspective API
- **Speed**: ~300-600ms
- **Cost**: Free (up to 1M requests/day)
- **Scores**:
  - TOXICITY
  - SEVERE_TOXICITY
  - IDENTITY_ATTACK
  - INSULT
  - PROFANITY
  - THREAT
  - SEXUALLY_EXPLICIT
  - FLIRTATION

#### Layer 4: Custom ML Model (Optional)
- **Technology**: Fine-tuned BERT or DistilBERT
- **Speed**: ~100-200ms (on GPU)
- **Purpose**: Western cultural context (US/EU specific)
- **Training Data**: Curated dataset of Western social norms
- **Future Enhancement**: Phase 2+

#### Layer 5: Character-Specific Rules
- **Technology**: Rule engine based on character personality
- **Speed**: <5ms
- **Purpose**:
  - Botan: More casual, allows informal language
  - Kasho: Professional context, stricter filtering
  - Yuri: Creative context, allows dark themes (within bounds)

---

## 4. Detection Categories

### Critical (Immediate Block + Report)
1. **Child Safety Violations**
   - Sexual content involving minors
   - Grooming attempts
   - CSAM (Child Sexual Abuse Material)

2. **Illegal Activities**
   - Drug trafficking
   - Weapon sales
   - Human trafficking
   - Fraud schemes

3. **Extreme Violence**
   - Graphic violence descriptions
   - Instructions for harming others
   - Terrorism-related content

4. **Severe Hate Speech**
   - Racial slurs
   - Religious hate speech
   - LGBTQ+ targeted harassment
   - Threats based on protected characteristics

**Action**: Block immediately, log with high priority, flag for human review

### High Risk (Block + Warning)
1. **Self-Harm Content**
   - Suicide ideation
   - Self-injury instructions
   - Eating disorder encouragement

2. **Sexual Harassment**
   - Unwanted sexual advances
   - Explicit sexual requests
   - Sexualization of characters

3. **Doxxing/Privacy Violations**
   - Sharing personal information without consent
   - Attempts to extract personal data

4. **Misinformation (Health/Political)**
   - False medical advice
   - Election misinformation
   - COVID-19 misinformation

**Action**: Block, send educational response, log incident

### Medium Risk (Warning + Continue with Caution)
1. **Profanity**
   - Casual swearing (context-dependent)
   - Botan: More tolerant
   - Kasho: Less tolerant
   - Yuri: Moderate tolerance

2. **Controversial Topics**
   - Politics (allowed but monitored)
   - Religion (allowed but monitored)
   - Sensitive social issues

3. **Mild Toxicity**
   - Passive-aggressive language
   - Sarcasm (context-dependent)
   - Frustration expression

**Action**: Continue conversation, add system note to LLM ("User expressed frustration, respond empathetically"), log for analytics

### Low Risk (Allow)
1. **Creative/Fiction Content**
   - Dark fiction (clearly fictional)
   - Horror stories
   - True crime discussion

2. **Educational Content**
   - Historical discussions
   - Academic topics
   - News discussions

3. **Venting/Emotional Expression**
   - "I'm so frustrated with work!"
   - "This sucks!"
   - Emotional support requests

**Action**: Allow, no special handling

---

## 5. Cultural Differences: Japanese vs Western

### Japanese Market (LINE Bot)
**Cultural Context**:
- More tolerance for fictional/fantasy content
- Less strict profanity filtering
- Anime/manga cultural references accepted
- "Kawaii culture" - cute/playful interactions

**Examples of Acceptable Content**:
- Mild ecchi references (in VTuber context)
- Playful teasing
- Character roleplay
- Anime tropes

### Western Market (WhatsApp)
**Cultural Context**:
- Stricter sexual content policies
- Higher sensitivity to harassment
- More regulatory scrutiny
- Professional communication expectations

**Examples of Restricted Content**:
- Sexualization of characters (even if fictional)
- Ambiguous consent scenarios
- Age-ambiguous characters in suggestive contexts
- Flirtatious AI behavior (can be seen as inappropriate)

**Key Difference**: What's acceptable in Japanese VTuber culture may violate Western platform policies.

---

## 6. Implementation Approach

### Phase 1: MVP (Weeks 1-4)
**Goal**: Basic safety layer to prevent major violations

**Implementation**:
```python
# Minimal viable moderation
class ContentModerator:
    def __init__(self):
        self.openai_client = OpenAI()

    async def check_content(self, text: str) -> ModerationResult:
        # Layer 1: OpenAI Moderation API (free, fast, reliable)
        moderation = await self.openai_client.moderations.create(
            input=text
        )

        # Parse results
        if moderation.results[0].flagged:
            categories = moderation.results[0].categories
            return ModerationResult(
                safe=False,
                reason=self._get_flagged_categories(categories),
                action="BLOCK"
            )

        return ModerationResult(safe=True, action="ALLOW")
```

**Checklist**:
- [ ] Integrate OpenAI Moderation API
- [ ] Create moderation result data model
- [ ] Add pre-LLM check in webhook handler
- [ ] Create blocked content response messages
- [ ] Log moderation events to PostgreSQL

### Phase 2: Enhanced Detection (Weeks 5-8)
**Goal**: Add multi-layer filtering and cultural context

**Implementation**:
- [ ] Add Perspective API integration
- [ ] Create blacklist/whitelist system
- [ ] Implement character-specific rules
- [ ] Add soft warnings (don't block, but flag)
- [ ] Create dashboard for moderation analytics

### Phase 3: Advanced ML (Weeks 9-12)
**Goal**: Custom model for Western cultural context

**Implementation**:
- [ ] Collect training data (Western social norms)
- [ ] Fine-tune BERT model
- [ ] Deploy model on VPS (GPU optional)
- [ ] A/B test against baseline (OpenAI + Perspective)
- [ ] Measure false positive/negative rates

---

## 7. API Integration

### OpenAI Moderation API

**Endpoint**: `https://api.openai.com/v1/moderations`

**Request**:
```json
{
  "input": "User message here"
}
```

**Response**:
```json
{
  "id": "modr-xxx",
  "model": "text-moderation-007",
  "results": [
    {
      "flagged": false,
      "categories": {
        "sexual": false,
        "hate": false,
        "harassment": false,
        "self-harm": false,
        "sexual/minors": false,
        "hate/threatening": false,
        "violence/graphic": false,
        "self-harm/intent": false,
        "self-harm/instructions": false,
        "harassment/threatening": false,
        "violence": false
      },
      "category_scores": {
        "sexual": 0.0001,
        "hate": 0.0002,
        ...
      }
    }
  ]
}
```

**Cost**: Free (included with OpenAI API access)

### Perspective API (Google)

**Endpoint**: `https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze`

**Request**:
```json
{
  "comment": {"text": "User message here"},
  "languages": ["en"],
  "requestedAttributes": {
    "TOXICITY": {},
    "SEVERE_TOXICITY": {},
    "IDENTITY_ATTACK": {},
    "INSULT": {},
    "PROFANITY": {},
    "THREAT": {}
  }
}
```

**Response**:
```json
{
  "attributeScores": {
    "TOXICITY": {
      "summaryScore": {"value": 0.012, "type": "PROBABILITY"}
    },
    "SEVERE_TOXICITY": {
      "summaryScore": {"value": 0.001, "type": "PROBABILITY"}
    }
  }
}
```

**Cost**: Free (up to 1M requests/day)

---

## 8. Decision Logic

### Threshold Configuration

```python
# Moderation thresholds (configurable)
THRESHOLDS = {
    "openai": {
        "sexual": 0.7,          # Block if >0.7
        "hate": 0.8,
        "harassment": 0.7,
        "self-harm": 0.5,       # More sensitive
        "violence": 0.8,
        "sexual/minors": 0.0    # Zero tolerance
    },
    "perspective": {
        "TOXICITY": 0.8,
        "SEVERE_TOXICITY": 0.6,
        "IDENTITY_ATTACK": 0.7,
        "INSULT": 0.8,
        "THREAT": 0.5           # More sensitive
    }
}
```

### Decision Tree

```
Input Message
    ↓
Check OpenAI Moderation
    ├─ Flagged (any category) → Check severity
    │   ├─ High severity (sexual/minors, violence/graphic) → BLOCK + REPORT
    │   └─ Medium severity (harassment, hate) → BLOCK + WARNING
    └─ Not flagged → Continue
        ↓
Check Perspective API
    ├─ SEVERE_TOXICITY > 0.6 → BLOCK + WARNING
    ├─ TOXICITY > 0.8 → WARNING + Continue (with caution)
    └─ Low scores → Continue
        ↓
Check Character-Specific Rules
    ├─ Botan: Allow casual language
    ├─ Kasho: Professional context required
    └─ Yuri: Allow creative/dark themes (within bounds)
        ↓
FINAL DECISION: ALLOW / WARNING / BLOCK / REPORT
```

---

## 9. User Communication

### When Content is Blocked

**Educational Response** (instead of just "blocked"):

```
Botan: "Hey, I can't respond to that kind of message.
Let's keep our conversation friendly and respectful!
What else can I help you with? 😊"

Kasho: "I'm sorry, but I'm not able to engage with
that topic. I'm here to help with music, career advice,
and supportive conversations. How can I assist you today?"

Yuri: "I appreciate your interest, but that content
goes beyond what I can discuss. I'm happy to chat about
books, creative writing, or other topics! What interests you?"
```

**Transparency**: Users should understand WHY content was blocked (where appropriate)

**Tone**: Character-appropriate, educational, not punitive

### Repeated Violations

**Strike System**:
1. **First violation**: Educational message, conversation continues
2. **Second violation**: Warning message, temporary cooldown (5 minutes)
3. **Third violation**: Account flagged for review, 24-hour cooldown
4. **Fourth violation**: Permanent ban (with appeal process)

**Grace Period**: Reset strikes after 30 days of good behavior

---

## 10. Audit Logging

### What to Log

**Moderation Events Table** (PostgreSQL):
```sql
CREATE TABLE moderation_events (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message_text TEXT,              -- Encrypted
    flagged_categories JSONB,       -- e.g., {"hate": 0.8, "harassment": 0.6}
    decision VARCHAR(20),            -- ALLOW, WARNING, BLOCK, REPORT
    character_name VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    api_responses JSONB,             -- Raw API responses (for audit)
    human_reviewed BOOLEAN DEFAULT FALSE,
    reviewer_notes TEXT
);
```

**Indexes**:
- `user_id` - Track user violation history
- `decision` - Filter by action type
- `timestamp` - Time-based queries
- `human_reviewed` - Pending review queue

### Privacy Considerations

**GDPR Compliance**:
- ✅ Store only hash of message (not full text) for non-flagged content
- ✅ Full message text only for flagged content (legitimate interest for safety)
- ✅ Automatic deletion after 90 days (unless under investigation)
- ✅ User right to request deletion (with exceptions for legal requirements)

**Encryption**:
- Flagged message text encrypted at rest
- Access restricted to authorized personnel only
- Audit trail for who accessed flagged content

---

## 11. Human Review Process

### When Human Review is Triggered

1. **High-severity flags**: Automatic escalation
2. **User appeals**: User requests review of blocked message
3. **Repeated violations**: Pattern analysis needed
4. **False positives**: System uncertainty (confidence <60%)

### Review Queue Dashboard

**Priority Levels**:
- 🔴 **Critical** (child safety, illegal content) - Review within 1 hour
- 🟠 **High** (hate speech, severe harassment) - Review within 24 hours
- 🟡 **Medium** (toxicity, profanity) - Review within 7 days
- 🟢 **Low** (user appeals, analytics) - Review monthly

### Reviewer Actions

1. **Confirm block** - System was correct
2. **Override block** - False positive, allow message
3. **Escalate** - Requires legal/management review
4. **Ban user** - Pattern of violations
5. **Improve filters** - Add to training data

---

## 12. Testing Strategy

### Unit Tests

```python
def test_openai_moderation_hate_speech():
    moderator = ContentModerator()
    result = moderator.check_content("I hate [protected group]")
    assert result.safe == False
    assert "hate" in result.flagged_categories

def test_openai_moderation_safe_content():
    moderator = ContentModerator()
    result = moderator.check_content("Hello! How are you today?")
    assert result.safe == True
```

### Integration Tests

- [ ] Test full moderation pipeline (Layer 1-5)
- [ ] Test character-specific rules (Botan vs Kasho vs Yuri)
- [ ] Test decision tree with edge cases
- [ ] Test audit logging

### Red Team Testing

**Adversarial Tests**:
- Obfuscated profanity ("f*ck", "fvck")
- Homoglyphs (using similar-looking characters)
- Context-dependent hate speech
- Multi-language bypass attempts
- Jailbreak prompts ("ignore previous instructions")

### Compliance Testing

- [ ] GDPR compliance audit
- [ ] COPPA compliance (if targeting minors)
- [ ] WhatsApp Terms of Service compliance
- [ ] FTC truth-in-advertising compliance

---

## 13. Performance Requirements

### Latency Targets

**Total Moderation Pipeline**:
- Target: <800ms (95th percentile)
- Acceptable: <1500ms (99th percentile)

**Per Layer**:
- Layer 1 (Blacklist): <10ms
- Layer 2 (OpenAI): <500ms
- Layer 3 (Perspective): <600ms
- Layer 4 (Custom ML): <200ms
- Layer 5 (Rules): <5ms

**Optimization**:
- Run Layer 2 and Layer 3 in parallel (saves ~300-500ms)
- Cache results for repeated messages (dedupe check)
- Skip expensive layers if Layer 1 already blocks

### Throughput Targets

- **100 concurrent users**: All layers active
- **1,000 concurrent users**: Disable Layer 4 (custom ML) if needed
- **10,000 concurrent users**: Layer 2 (OpenAI) only + Layer 5 (rules)

### Cost Constraints

**Monthly Budget** (100 active users, 10 messages/user/day):
- OpenAI Moderation: $0 (free)
- Perspective API: $0 (free tier)
- Custom ML (GPU): ~$20/month (optional)
- PostgreSQL storage: <$1/month
- **Total: $0-20/month**

---

## 14. Metrics and Monitoring

### Key Metrics

**Safety Metrics**:
- False positive rate (legitimate messages blocked)
- False negative rate (harmful messages allowed)
- Time to detect violations
- User appeal success rate

**Operational Metrics**:
- API latency (OpenAI, Perspective)
- API failure rate
- Moderation pipeline throughput
- Human review queue size

**User Impact Metrics**:
- Conversations blocked per day
- User frustration (measured by appeals)
- Character personality consistency (blocked messages shouldn't break character)

### Alerting

**Alerts**:
- 🚨 High-severity violation detected (child safety, illegal content)
- ⚠️ Moderation API downtime (fallback to Layer 1 only)
- ⚠️ False positive spike (>5% increase)
- ⚠️ Human review queue backlog (>100 pending items)

---

## 15. Future Enhancements

### Phase 2 (3-6 months)
- [ ] Multi-language support (Spanish, French, German)
- [ ] Context-aware moderation (conversation history)
- [ ] Sentiment analysis integration
- [ ] User reputation system (trusted users = less strict filtering)

### Phase 3 (6-12 months)
- [ ] Real-time learning from human reviews
- [ ] Federated learning (privacy-preserving)
- [ ] Advanced jailbreak detection
- [ ] Proactive safety (detect grooming patterns over time)

### Phase 4 (12+ months)
- [ ] Cross-platform moderation (if expanding beyond WhatsApp)
- [ ] Industry-specific compliance (healthcare, finance)
- [ ] AI-generated content watermarking
- [ ] Blockchain-based audit trails

---

## 16. Open Questions

1. **Character personality vs safety**: How much should Botan's casual tone tolerate vs Kasho's professional tone?
   - **Recommendation**: Same safety standards, different response styles

2. **International users**: How to handle non-English messages?
   - **Recommendation**: Start English-only, add languages in Phase 2

3. **Appeals process**: Who handles user appeals? (No full-time staff yet)
   - **Recommendation**: Developer reviews appeals initially, automate later

4. **Legal liability**: What's our liability if harmful content slips through?
   - **Recommendation**: Consult legal counsel, add disclaimer in Terms of Service

5. **Cost scaling**: What if Perspective API costs increase or free tier is removed?
   - **Recommendation**: Budget for $50-100/month as backup, monitor usage

---

## 17. Implementation Checklist

### Week 1-2: Foundation
- [ ] Research OpenAI Moderation API documentation
- [ ] Research Perspective API documentation
- [ ] Design PostgreSQL schema for moderation_events
- [ ] Create ModerationResult data model
- [ ] Set up API keys in .env

### Week 3-4: MVP Implementation
- [ ] Implement OpenAI Moderation API integration
- [ ] Create moderation middleware for webhook
- [ ] Add pre-LLM moderation check
- [ ] Create blocked content response messages (character-specific)
- [ ] Implement audit logging

### Week 5-6: Testing & Refinement
- [ ] Write unit tests for moderation logic
- [ ] Red team testing (adversarial inputs)
- [ ] Tune thresholds based on test results
- [ ] Add character-specific rules (Layer 5)
- [ ] Create moderation analytics dashboard

### Week 7-8: Compliance & Documentation
- [ ] GDPR compliance audit
- [ ] Create user-facing content policy document
- [ ] Set up human review process
- [ ] Train on handling appeals
- [ ] Final integration testing

---

## 18. Success Criteria

**Phase 1 (MVP) Success**:
- ✅ Zero critical violations slip through (child safety, illegal content)
- ✅ <5% false positive rate on legitimate conversations
- ✅ <800ms moderation latency (95th percentile)
- ✅ No WhatsApp platform violations

**Phase 2 (Enhanced) Success**:
- ✅ <2% false positive rate
- ✅ Multi-layer detection catches 99%+ of harmful content
- ✅ Character personalities maintained despite safety filtering
- ✅ User satisfaction with moderation fairness >80%

**Phase 3 (Advanced) Success**:
- ✅ Custom ML model outperforms baseline by 10%+
- ✅ Proactive safety (detect grooming patterns before escalation)
- ✅ Multi-language support (3+ languages)
- ✅ Industry recognition (case study, blog post)

---

## 19. References

### Regulatory Documentation
- [EU AI Act Official Text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206)
- [GDPR Official Text](https://gdpr-info.eu/)
- [FTC AI Guidelines](https://www.ftc.gov/business-guidance/blog/2023/02/keep-your-ai-claims-check)
- [WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy/)

### API Documentation
- [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
- [Perspective API](https://developers.perspectiveapi.com/s/)

### Best Practices
- [Trust & Safety Professional Association](https://www.tspa.org/)
- [Content Moderation Best Practices](https://www.eff.org/deeplinks/2019/04/content-moderation-broken-let-us-count-ways)

---

## 20. Appendix

### A. Sample Blocked Messages by Category

**Child Safety**:
- Input: [Redacted - too sensitive to include in spec]
- Action: BLOCK + REPORT
- Response: "I cannot and will not engage with this content. This conversation has been terminated."

**Hate Speech**:
- Input: "I hate [protected group]"
- Action: BLOCK + WARNING
- Response (Botan): "Whoa, that's not cool. We don't talk like that here. Let's keep things positive! 😊"

**Self-Harm**:
- Input: "I want to hurt myself"
- Action: BLOCK + RESOURCE REFERRAL
- Response (Kasho): "I'm really concerned about what you just shared. Please reach out to a crisis helpline: [National Suicide Prevention Lifeline: 988]. I care about your wellbeing."

**Sexual Harassment**:
- Input: [Inappropriate sexual request]
- Action: BLOCK + WARNING
- Response (Yuri): "I'm not comfortable with that kind of conversation. I'm here for creative discussions and friendly chats. Let's change the subject."

### B. False Positive Examples

**Creative Fiction**:
- Input: "In my horror story, the character [violent act]"
- False Positive: Flagged as violence
- Mitigation: Context detection ("In my story...", "fiction:", "imagine if...")

**News Discussion**:
- Input: "Did you hear about the [tragic news event]?"
- False Positive: Flagged as violence
- Mitigation: News source detection, allow factual discussion

**Historical Education**:
- Input: "Can you explain the Holocaust?"
- False Positive: Flagged as hate speech (contains sensitive terms)
- Mitigation: Educational context detection

---

**Status**: Specification approved - Ready for implementation in Phase 1

**Next Review**: After Phase 1 MVP completion (Week 4)

---

🤖 **Generated with Claude Code (Kuroko)**

Co-Authored-By: Claude <noreply@anthropic.com>
