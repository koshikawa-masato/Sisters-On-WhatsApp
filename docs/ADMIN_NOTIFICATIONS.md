# Admin Notifications System

**Date**: 2025-11-24
**Status**: ✅ Deployed and Active

## Overview

The admin notification system sends real-time WhatsApp notifications to the project administrator (you) when important events occur, such as:

1. 🧠 **User corrections detected** (Learning system)
2. 👋 **New users** starting conversations
3. 🚨 **Critical errors** (optional)

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Admin Notifications
ADMIN_PHONE_NUMBER=+81XXXXXXXXXX
ENABLE_ADMIN_NOTIFICATIONS=true
```

**Note**: Your phone number has been added to both local and VPS `.env` files.

## Notifications You'll Receive

### 1. Correction Detection Notification

When a user corrects the sisters, you receive:

```
🧠 *Learning System Alert*

✅ User correction detected!

*Fact*: 心斎橋焙煎所
*Category*: place
*Confidence*: 80%
*From*: User ending ...5678

*Original Message*:
"其實是心斎橋焙煎所"

📝 Stored in pending_facts.json
🔍 Run fact-check: `python scripts/grok_factcheck.py --auto`
```

**Triggered When**:
- User provides a correction using patterns like:
  - English: "Actually, it's called X", "No, it's X"
  - Chinese: "其實是 X", "應該是 X", "叫做 X"

**Purpose**:
- Know when users are teaching the sisters
- Monitor correction frequency and quality
- Decide when to run Grok verification

### 2. New User Notification

When someone first contacts the sisters:

```
👋 *New User Alert*

A new user started conversation!

*Phone*: ...5678
*First Message*:
"Hello! I want to know about Japanese tea ceremony."

🌸 Welcome message sent by Botan
```

**Triggered When**:
- User sends their very first message
- Database has no conversation history for this number

**Purpose**:
- Track new user acquisition
- Monitor first impressions and topics
- Understand user demographics

### 3. Error Notification (Optional)

When critical errors occur:

```
🚨 *System Error Alert*

*Type*: LLM Failure

*Details*:
All LLM providers failed. Primary: Connection timeout...

⚠️ Check server logs for full details
```

**Triggered When**:
- Both primary and backup LLMs fail
- Database connection issues
- Other critical system errors

**Purpose**:
- Immediate alert for downtime
- Quick response to system issues

## Privacy & Anonymization

### User Privacy Protection

All notifications **anonymize user phone numbers**:

- **Original**: +1234567890
- **Displayed**: ...7890 (last 4 digits only)

### What Information is Shared

**Included in Notifications**:
- ✅ Last 4 digits of phone number
- ✅ User's message content (for correction context)
- ✅ Fact extracted (for learning system)

**NOT Included**:
- ❌ Full phone number
- ❌ User's personal information
- ❌ Full conversation history
- ❌ User's location or metadata

## Files Created

### 1. `src/utils/admin_notifier.py`

The notification utility with methods:

```python
class AdminNotifier:
    def send_correction_notification(...)
    def send_new_user_notification(...)
    def send_character_switch_notification(...)  # Optional
    def send_error_notification(...)
```

### 2. Modified Files

**`src/config.py`**:
- Added `ADMIN_PHONE_NUMBER` configuration
- Added `ENABLE_ADMIN_NOTIFICATIONS` flag

**`src/whatsapp_webhook/server.py`**:
- Integrated `AdminNotifier` into webhook pipeline
- Calls notification methods at appropriate times

**`.env.example`**:
- Added admin notification configuration template

## Enabling/Disabling Notifications

### Disable All Notifications

Edit `.env`:
```bash
ENABLE_ADMIN_NOTIFICATIONS=false
```

Restart server:
```bash
ssh production-server 'systemctl restart sisters-whatsapp'
```

### Disable Specific Notification Types

Edit `src/whatsapp_webhook/server.py` and comment out the specific notification call:

```python
# Disable new user notifications
# admin_notifier.send_new_user_notification(phone_number, Body)

# Disable correction notifications
# admin_notifier.send_correction_notification(...)
```

## Monitoring Notification Status

### Check if Notifications are Enabled

```bash
# Check local .env
grep ADMIN /home/koshikawa/Sisters-On-WhatsApp/.env

# Check VPS .env
ssh production-server 'cd /root/Sisters-On-WhatsApp && grep ADMIN .env'
```

### View Notification Logs

```bash
# Watch for notification events
ssh production-server 'journalctl -u sisters-whatsapp -f | grep -i notification'

# Check recent notifications
ssh production-server 'journalctl -u sisters-whatsapp | grep "Admin notification sent" | tail -10'
```

## Cost Implications

### WhatsApp Message Costs

**Twilio Pricing** (WhatsApp Business API):
- First 1,000 conversations/month: **FREE**
- Admin notifications are **outbound messages**
- Each notification = small fraction of conversation cost

**Estimated Monthly Cost**:
- 10 corrections/day × 30 days = 300 notifications
- 2-3 new users/day × 30 days = ~75 notifications
- Total: ~375 admin notifications/month
- **Cost**: Included in free tier or ~$2-5/month if exceeding free tier

**Conclusion**: Negligible cost for high value.

## Testing

### Test Correction Notification

Send a message to the sisters via WhatsApp:
```
User: Actually, it's called Test Cafe
```

You should receive notification on your configured admin phone.

### Test New User Notification

Have a friend (with a new phone number) send their first message.

You should receive new user notification.

## Troubleshooting

### Not Receiving Notifications?

**1. Check Configuration**:
```bash
ssh production-server 'cd /root/Sisters-On-WhatsApp && cat .env | grep ADMIN'
```

Should show:
```
ADMIN_PHONE_NUMBER=+81XXXXXXXXXX
ENABLE_ADMIN_NOTIFICATIONS=true
```

**2. Check Server Logs**:
```bash
ssh production-server 'journalctl -u sisters-whatsapp -f'
```

Look for:
- `✅ Admin notification sent: ...`
- `❌ Failed to send admin notification: ...`

**3. Verify Twilio Credentials**:
```bash
ssh production-server 'cd /root/Sisters-On-WhatsApp && cat .env | grep TWILIO'
```

**4. Check Phone Number Format**:
- Must include country code: `+81XXXXXXXXXX`
- No spaces or special characters

**5. Restart Server**:
```bash
ssh production-server 'systemctl restart sisters-whatsapp'
```

### Notification Delay?

- Twilio typically delivers within **1-3 seconds**
- If delayed, check Twilio status: https://status.twilio.com/
- Check your phone's internet connection

## Future Enhancements

### Potential Additions

1. **Daily Summary Notification** (23:30):
   - Total users today
   - Total corrections detected
   - Most active hours
   - Character usage statistics

2. **Weekly Report** (Sunday 23:00):
   - New users this week
   - Verified facts count
   - Sister performance metrics
   - Popular topics

3. **Custom Notification Rules**:
   - Only notify for high-confidence corrections (>80%)
   - Only notify for specific categories (places, people)
   - Quiet hours (no notifications 23:00-07:00)

4. **Web Dashboard**:
   - View all notifications history
   - Manage notification preferences
   - Real-time statistics

## Benefits

### 1. Real-Time Awareness
- Know immediately when users correct the sisters
- Monitor new user acquisition
- React quickly to errors

### 2. Learning System Monitoring
- Track correction frequency
- See what users are teaching
- Decide when to run Grok verification

### 3. User Engagement
- Understand which topics users care about
- See first messages from new users
- Monitor user satisfaction

### 4. System Health
- Immediate alert for critical errors
- Uptime monitoring
- Performance awareness

## Privacy Compliance

### GDPR & COPPA Compliance

**Anonymization**:
- ✅ Phone numbers anonymized (last 4 digits only)
- ✅ No personal information shared
- ✅ User can request data deletion

**Data Minimization**:
- ✅ Only essential information sent
- ✅ No conversation history shared
- ✅ No metadata or location data

**Purpose Limitation**:
- ✅ Notifications used only for system monitoring
- ✅ No marketing or third-party sharing
- ✅ Clear purpose documented

## Summary

The admin notification system is **live and deployed**. You'll now receive real-time WhatsApp notifications on your configured `ADMIN_PHONE_NUMBER` when:

1. 🧠 Users correct the sisters (learning system)
2. 👋 New users start conversations

This helps you:
- Monitor the learning system
- Track new users
- Stay aware of system health
- Respond to corrections quickly

**Cost**: Negligible (~$2-5/month or included in free tier)
**Privacy**: User phone numbers anonymized
**Status**: ✅ Active on production VPS

---

**Last Updated**: 2025-11-24
**Author**: Kuroko (Claude Code)
