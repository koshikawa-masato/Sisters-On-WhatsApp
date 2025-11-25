# Security Architecture - Sisters-On-WhatsApp

## Overview

This document describes the security architecture implemented in Sisters-On-WhatsApp, including encryption, key management, and recommendations for further hardening.

---

## Current Security Implementation (Level 1)

### Encryption

| Data Type | Method | Algorithm |
|-----------|--------|-----------|
| Phone numbers | Encryption | AES-256 (Fernet) |
| Conversation content | Encryption | AES-256 (Fernet) |
| Phone lookup | Hash | SHA-256 |

### How It Works

```
User Phone: +1234567890
    ↓
Encrypted: Z0FBQUFBQnBKV0UtM2pKNmZjOWJH...  (stored in DB)
Hash:      1ebe730d9863905dddbb9cf14b5ec0e...  (for lookup)
```

### Key Storage

- `ENCRYPTION_KEY` stored in `.env` (gitignored)
- Key format: Fernet-compatible base64 string
- Generated once, used for all encryption/decryption

### What's Protected

| Table | Encrypted Columns |
|-------|-------------------|
| `conversation_history` | `phone_number`, `content` |
| `user_sessions` | `phone_number` |
| `user_consents` | `phone_number` |

### What Attackers See (DB Access Only)

```sql
-- Raw database query result:
SELECT phone_number, content FROM conversation_history LIMIT 1;

phone_number                              | content
------------------------------------------+------------------------------------------
Z0FBQUFBQnBKV0UtM2pKNmZjOWJHZzFDRUdxWm9X | Z0FBQUFBQnBKV0UtaF9VRFpuY0ZvTm5KS3lDR0Zu
```

**Without the encryption key, this data is unreadable.**

---

## Decryption Requirements

To decrypt data, an attacker needs ALL of the following:

1. **`.env` file** - Contains `ENCRYPTION_KEY`
2. **`src/privacy/encryption.py`** - Decryption logic
3. **Python environment** - With `cryptography` library
4. **Database access** - To retrieve encrypted data

### Security Layers

```
GitHub (public)  → Code only, no keys
VPS (private)    → .env + code + DB
Local (private)  → .env + code
```

**Single point of failure: VPS compromise**

---

## Security Levels & Recommendations

### Level 1: Current Implementation ✅

- [x] AES-256 encryption for PII
- [x] SHA-256 hash for lookups
- [x] Key stored in `.env` (gitignored)
- [x] HTTPS via Twilio (webhook)
- [x] SSH key-only authentication (password disabled)
- [x] fail2ban (brute force protection)

**Suitable for:** Personal projects, MVP, small startups

---

### Level 2: Key Management Enhancement

| Measure | Description | Cost |
|---------|-------------|------|
| **AWS KMS / GCP KMS** | Cloud-managed keys, never stored on VPS | $1-3/month |
| **HashiCorp Vault** | Self-hosted secret management | Free (operational cost) |
| **Key rotation script** | Periodic key changes | Free |

**Implementation example (AWS KMS):**
```python
import boto3

kms = boto3.client('kms')
# Key never leaves AWS
encrypted = kms.encrypt(KeyId='alias/sisters-key', Plaintext=data)
decrypted = kms.decrypt(CiphertextBlob=encrypted['CiphertextBlob'])
```

---

### Level 3: Infrastructure Hardening

| Measure | Description | Cost |
|---------|-------------|------|
| **VPN-only SSH** | SSH access only via VPN | $5-10/month |
| **Firewall rules** | Allow only necessary ports | Free |
| **SSH 2FA** | Google Authenticator | Free |
| **Audit logging** | Log all access attempts | Free |
| **Fail2ban** | Block brute force attempts | Free |

**Quick wins (free):**
```bash
# Enable 2FA for SSH
sudo apt install libpam-google-authenticator
google-authenticator

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

### Level 4: Enterprise Grade

| Measure | Description | Cost |
|---------|-------------|------|
| **HSM** | Hardware Security Module | $500+/month |
| **Zero Trust Architecture** | Verify all access | High |
| **SOC2 / ISO27001** | Security audit certification | $10,000+ |
| **Penetration testing** | Professional security audit | $5,000+ |

**Required for:** Enterprise customers, regulated industries (healthcare, finance)

---

## Recommended Next Steps

### Priority 1: Quick & Free ✅ DONE

1. ~~**Enable SSH 2FA**~~ → Optional (recommended for high-security)
   ```bash
   sudo apt install libpam-google-authenticator
   ```

2. **Enable fail2ban** ✅ Implemented (2025-11-25)
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

3. **Restrict SSH to key-only** ✅ Already configured
   ```bash
   # /etc/ssh/sshd_config
   PasswordAuthentication no
   ```

### Priority 2: Key Rotation

Create a key rotation script:
```python
# scripts/rotate_encryption_key.py
# 1. Generate new key
# 2. Re-encrypt all data with new key
# 3. Update .env
# 4. Restart service
```

### Priority 3: Cloud KMS (If Scaling)

Migrate to AWS KMS or GCP KMS when:
- Handling >10,000 users
- Enterprise customers require it
- Compliance requirements (HIPAA, PCI-DSS)

---

## Threat Model

| Threat | Mitigation | Status |
|--------|------------|--------|
| DB breach | AES-256 encryption | ✅ |
| Code leak (GitHub) | No secrets in code | ✅ |
| VPS compromise | SSH key-only, fail2ban | ✅ |
| Man-in-the-middle | HTTPS (Twilio) | ✅ |
| Brute force | fail2ban | ✅ |
| SSH 2FA | Google Authenticator | ⚠️ Recommended |
| Key theft | KMS | ⏳ Future |

---

## Files & Locations

| File | Purpose | Public |
|------|---------|--------|
| `src/privacy/encryption.py` | Encryption/decryption logic | Yes (GitHub) |
| `.env` | Contains `ENCRYPTION_KEY` | No (gitignored) |
| `scripts/encrypt_existing_data.py` | Migration script | No (gitignored) |

---

## Compliance Notes

### GDPR (EU)
- ✅ Data encryption at rest
- ✅ Right to deletion (`DELETE` command)
- ✅ Data export (`EXPORT` command)
- ✅ Consent tracking

### CCPA (California)
- ✅ Data deletion on request
- ✅ No data sales

### Best Practices
- ✅ Minimal data collection
- ✅ 90-day retention policy
- ✅ Encrypted storage

---

## Summary

| Level | Security | Cost | Use Case |
|-------|----------|------|----------|
| **1+ (Current)** | AES-256 + Hash + fail2ban + SSH key-only | Free | Personal/MVP |
| **2** | + Cloud KMS | $1-3/mo | Startup |
| **3** | + SSH 2FA + VPN | $5-10/mo | Growth |
| **4** | + HSM + SOC2 | $10,000+ | Enterprise |

**Current status: Level 1+ - Enhanced security with fail2ban and SSH hardening. Sufficient for personal projects and small-scale production.**

---

*Last updated: 2025-11-25*
