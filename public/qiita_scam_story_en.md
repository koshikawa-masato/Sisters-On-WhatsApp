# A Scammer Debugged My AI Bot for Free and Left Their Phone Number Permanently in Git History

## TL;DR

- Got a LinkedIn DM from a "Taiwanese beauty" (self-proclaimed) → Investment scam
- They "helpfully" tested my WhatsApp bot under development
- Showed the chat logs to Claude Opus 4.5 → "100% scam" verdict in 0.2 seconds
- Fatal mistake: Called a ¥300,000 PRADA hoodie "something I bought online"
- Result: $0 lost, but the scammer's Hong Kong number is now permanently in Git history (undeletable)

The ultimate reversal.

---

## Chapter 1: The Hook

A message appeared on LinkedIn from "Enya" (pseudonym) — perfect café photo, flawless smile.
Occupation: Owner of a famous café chain. Location: Taiwan. Hobbies: Japanese culture. Age: Eternally 25 (probably).

"Your 50 years of engineering experience is so fascinating! ♡"
→ Yes, I took the bait (briefly).

Immediately suggested moving to LINE → Deleted LinkedIn account right after.
Textbook scam manual page 1: "Destroy evidence immediately." I was almost impressed.

---

## Chapter 2: Free QA Engineer Appears

I mentioned my project "Sisters-On-WhatsApp" (a WhatsApp bot where three AI sisters chat with users).

"That sounds fun! Let me test it!"

They voluntarily registered for my Twilio Sandbox. Divine intervention.
And they actually found a bug.

```
Enya: This thing's stuck in an infinite loop
Me: Holy shit you're a god, thank you
```

I was so grateful I put their name in my commit message.

```bash
git commit -m "Fix infinite welcome loop - Discovered by lovely tester Enya 🌹 (+852-XXXX-XXXX)"
```

...And that's when the scammer etched their phone number into Git.
Try to delete it? GitHub says "Force push? Nah ♪" — It's there forever.

---

## Chapter 3: Here Comes the Investment Pitch!

One day, the conversation suddenly shifted.

"Isn't the weak yen scary? I'm making ¥3 million monthly from crypto ♡"
"I'll share some pre-IPO gems with you, let's get rich together ♡"

...???
That doesn't work on a 50-year-old guy. Sorry.

I dumped all the chat logs into Claude Opus 4.5 (Anthropic's latest and most powerful reasoning model).

**Claude Opus 4.5's response (0.18 seconds later):**

> "This is 100% a pig butchering scam. Run."

Cold and perfect. The moment AI rejected my "girlfriend."

Fun fact: Opus 4.5 was released in February 2025, specializing in complex reasoning and coding. Pattern recognition for scams? Child's play.

---

## Chapter 4: PRADA Settles Everything

The profile photo showed obviously expensive clothing. Time for a little jab.

Me: "Nice hoodie, what brand is it?"
Enya: "It's not a brand~ Just something I bought from an online shop!"

...Case closed.
That hoodie: PRADA 2024AW Geometric Hoodie, retail price ¥298,000 (~$2,000).

**No human on Earth casually calls a $2,000 PRADA hoodie "something from online shopping."**

This is mathematically provable:

```python
if person.owns(PRADA_2000_dollar_hoodie):
    person.knows_price() == True
    person.says("online shopping") == False
else:
    person == photo_theft_scammer
# Q.E.D.
```

Columbo: "Just one more thing..."

---

## Chapter 5: The Scammer's Legacy (Permanently Archived)

| What the scammer intended | What actually happened |
|---------------------------|------------------------|
| Steal money | $0 lost, they fixed my bug instead |
| Destroy evidence | Phone number permanently etched in Git |
| Stay anonymous | Got their burner phone number! |
| Pretend to be a cute woman | Didn't fool someone with 50 years of reading people |

The GitHub commit log still shines bright:

```
$ git log --oneline
a1b2c3d Fix infinite loop - thanks Enya (+852-XXXX-XXXX) 🌹
```

Scammer Hall of Fame inductee confirmed.

---

## Why I Didn't Get Scammed (Humble Brag)

1. **50 years of analyzing conversation logs**
   From the PC communication era, I developed the skill to detect gender, age, and income from writing style alone

2. **Admitting when I don't understand**
   "Making ¥3 million from crypto" made zero sense to me, so I didn't even try to understand (this is key)

3. **Claude Opus 4.5: The cold-blooded partner**
   Where a human might say "well, maybe they're just like that," AI immediately declares "It's a scam." Anthropic's flagship model doesn't do sympathy

4. **Unconscious Socratic questioning**
   50 years of habit: "Pretend you don't know and let them talk"

---

## A Thank You to the Scammer

Enya (real name unknown), thank you so much.

Thanks to you:
- Fixed 1 bug
- Got the best blog content ever
- Your phone number is now part of internet history
- Trending on Qiita guaranteed

You were the ultimate **unpaid intern**.

---

## Technical Notes

### Tech Stack
- **WhatsApp Bot**: WhatsApp Business API + Twilio Sandbox + FastAPI
- **LLM**: Kimi (Moonshot AI) + GPT-4o-mini (production)
- **Development Partner**: Claude Code (Claude Opus 4.5) - Scam detection duty

### About Claude Opus 4.5

Anthropic's latest and most powerful model, released February 2025.

- **Official name**: claude-opus-4-5-20251101
- **Features**: Extended Thinking for deep reasoning capabilities
- **Strengths**: Coding, complex analysis, pattern recognition
- **Today's highlight**: Detected scam pattern from chat logs in 0.18 seconds

The ability to instantly identify scam tactics through pattern matching proves the power of combining 50 years of human experience with cutting-edge AI.

### Repository

- GitHub: [Sisters-On-WhatsApp](https://github.com/koshikawa-masato/Sisters-On-WhatsApp)
- The scammer's phone number is still visible in `git log`

---

**Total damage: $0**
**What I gained: A legend**

Enya, keep up the good work from Hong Kong.
Your phone number? It's not going anywhere ♡

---

#scam #LinkedInScam #PigButchering #GitIsJustice #PRADA #ClaudeOpus #AI #CyberSecurity
