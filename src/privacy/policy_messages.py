"""
Privacy Policy Messages - Multi-region support

Supports: EU (GDPR), US (CCPA), Taiwan (PDPA), China (PIPL)
"""

from typing import Dict, Optional
from enum import Enum


class Region(Enum):
    """Supported regulatory regions."""
    EU = "eu"           # GDPR
    US = "us"           # CCPA/CPRA
    TAIWAN = "taiwan"   # PDPA
    CHINA = "china"     # PIPL
    DEFAULT = "default" # International fallback


# Phone number prefixes to region mapping
PHONE_PREFIX_TO_REGION = {
    # EU countries
    "+43": Region.EU,   # Austria
    "+32": Region.EU,   # Belgium
    "+359": Region.EU,  # Bulgaria
    "+385": Region.EU,  # Croatia
    "+357": Region.EU,  # Cyprus
    "+420": Region.EU,  # Czech Republic
    "+45": Region.EU,   # Denmark
    "+372": Region.EU,  # Estonia
    "+358": Region.EU,  # Finland
    "+33": Region.EU,   # France
    "+49": Region.EU,   # Germany
    "+30": Region.EU,   # Greece
    "+36": Region.EU,   # Hungary
    "+353": Region.EU,  # Ireland
    "+39": Region.EU,   # Italy
    "+371": Region.EU,  # Latvia
    "+370": Region.EU,  # Lithuania
    "+352": Region.EU,  # Luxembourg
    "+356": Region.EU,  # Malta
    "+31": Region.EU,   # Netherlands
    "+48": Region.EU,   # Poland
    "+351": Region.EU,  # Portugal
    "+40": Region.EU,   # Romania
    "+421": Region.EU,  # Slovakia
    "+386": Region.EU,  # Slovenia
    "+34": Region.EU,   # Spain
    "+46": Region.EU,   # Sweden
    "+44": Region.EU,   # UK (still follows similar standards)

    # US
    "+1": Region.US,

    # Taiwan
    "+886": Region.TAIWAN,

    # China
    "+86": Region.CHINA,

    # Hong Kong, Macau (follow similar to China/Taiwan)
    "+852": Region.TAIWAN,  # Hong Kong - closer to Taiwan regulations
    "+853": Region.CHINA,   # Macau

    # Singapore (PDPA similar to Taiwan)
    "+65": Region.TAIWAN,

    # Japan (APPI - similar approach to EU)
    "+81": Region.EU,
}


class PrivacyPolicyMessages:
    """Multi-region privacy policy messages."""

    # Privacy policy URLs (hosted on GitHub Pages)
    # Repository: https://github.com/koshikawa-masato/sisters-whatsapp-privacy
    POLICY_URLS = {
        Region.EU: "https://sisters-whatsapp.com/privacy/eu.html",
        Region.US: "https://sisters-whatsapp.com/privacy/us.html",
        Region.TAIWAN: "https://sisters-whatsapp.com/privacy/tw.html",
        Region.CHINA: "https://sisters-whatsapp.com/privacy/cn.html",
        Region.DEFAULT: "https://sisters-whatsapp.com",
    }

    # Initial consent messages by region
    CONSENT_MESSAGES = {
        Region.EU: {
            "en": """👋 *Welcome to Sisters-On-WhatsApp!*

We're three AI sisters who can help you:
🌸 *Botan* - Streaming & pop culture
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

🔒 *Privacy Notice (GDPR)*
Before we chat, please read our privacy practices:

*What we collect:*
• Your phone number (for identification)
• Conversation history (to maintain context)
• Language preference

*Your rights:*
• Access your data anytime
• Request data deletion
• Export your data
• Withdraw consent

*Data protection:*
• Encrypted storage (AES-256)
• No sharing with third parties
• Data retained for 90 days of inactivity

📋 Full policy: {policy_url}

Reply *AGREE* to continue, or *DECLINE* to opt out.
Reply *DELETE* anytime to erase your data.""",

            "zh": """👋 *歡迎來到Sisters-On-WhatsApp！*

我們是三位AI姐妹：
🌸 *牡丹* - 直播與流行文化
🎵 *芍藥* - 音樂與人生建議
📚 *百合* - 書籍與創意思考

🔒 *隱私聲明 (GDPR)*
在開始聊天之前，請閱讀我們的隱私條款：

*我們收集的資料：*
• 您的電話號碼（用於識別）
• 對話記錄（用於維持對話情境）
• 語言偏好

*您的權利：*
• 隨時存取您的資料
• 要求刪除資料
• 匯出您的資料
• 撤回同意

*資料保護：*
• 加密儲存 (AES-256)
• 不與第三方分享
• 資料在90天無活動後刪除

📋 完整條款：{policy_url}

回覆 *AGREE* 繼續，或 *DECLINE* 選擇退出。
隨時回覆 *DELETE* 可刪除您的資料。"""
        },

        Region.US: {
            "en": """👋 *Welcome to Sisters-On-WhatsApp!*

We're three AI sisters who can help you:
🌸 *Botan* - Streaming & pop culture
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

🔒 *Privacy Notice (CCPA/CPRA)*
Here's how we handle your information:

*Information collected:*
• Phone number (identification)
• Conversation history (context)
• Language preference

*Your California rights:*
• Know what data we collect
• Delete your data
• Opt-out of data sales (we don't sell data)
• Non-discrimination

*Security:*
• Encrypted storage (AES-256)
• No third-party sharing
• 90-day retention policy

📋 Full policy: {policy_url}

Reply *AGREE* to continue, or *DECLINE* to opt out.
Reply *DELETE* anytime to erase your data.""",

            "zh": """👋 *歡迎來到Sisters-On-WhatsApp！*

我們是三位AI姐妹：
🌸 *牡丹* - 直播與流行文化
🎵 *芍藥* - 音樂與人生建議
📚 *百合* - 書籍與創意思考

🔒 *隱私聲明 (CCPA/CPRA)*
以下是我們處理您資訊的方式：

*收集的資訊：*
• 電話號碼（識別用途）
• 對話記錄（情境維持）
• 語言偏好

*您的加州權利：*
• 了解我們收集的資料
• 刪除您的資料
• 選擇退出資料銷售（我們不銷售資料）
• 不受歧視

*安全措施：*
• 加密儲存 (AES-256)
• 不與第三方分享
• 90天保留政策

📋 完整條款：{policy_url}

回覆 *AGREE* 繼續，或 *DECLINE* 選擇退出。
隨時回覆 *DELETE* 可刪除您的資料。"""
        },

        Region.TAIWAN: {
            "en": """👋 *Welcome to Sisters-On-WhatsApp!*

We're three AI sisters who can help you:
🌸 *Botan* - Streaming & pop culture
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

🔒 *Privacy Notice (Taiwan PDPA)*
Please review our data practices:

*Data collected:*
• Phone number (identification)
• Conversation history (service provision)
• Language preference

*Your rights under PDPA:*
• Access and review your data
• Request corrections
• Request deletion
• Refuse marketing use

*Protection measures:*
• Encrypted storage (AES-256)
• No third-party disclosure
• Data deleted after 90 days of inactivity

📋 Full policy: {policy_url}

Reply *AGREE* to continue, or *DECLINE* to opt out.
Reply *DELETE* anytime to erase your data.""",

            "zh": """👋 *歡迎來到Sisters-On-WhatsApp！*

我們是三位AI姐妹：
🌸 *牡丹* - 直播與流行文化
🎵 *芍藥* - 音樂與人生建議
📚 *百合* - 書籍與創意思考

🔒 *隱私聲明（台灣個資法）*
請閱讀我們的資料處理方式：

*收集的資料：*
• 電話號碼（識別用途）
• 對話記錄（服務提供）
• 語言偏好

*您依個資法享有的權利：*
• 存取及檢視您的資料
• 要求更正
• 要求刪除
• 拒絕行銷使用

*保護措施：*
• 加密儲存 (AES-256)
• 不對第三方揭露
• 資料在90天無活動後刪除

📋 完整條款：{policy_url}

回覆 *AGREE* 繼續，或 *DECLINE* 選擇退出。
隨時回覆 *DELETE* 可刪除您的資料。"""
        },

        Region.CHINA: {
            "en": """👋 *Welcome to Sisters-On-WhatsApp!*

We're three AI sisters who can help you:
🌸 *Botan* - Streaming & pop culture
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

🔒 *Privacy Notice (PIPL)*
Please review our data practices:

*Personal information collected:*
• Phone number (identification)
• Conversation history (service)
• Language preference

*Your rights under PIPL:*
• Access your personal information
• Request corrections
• Request deletion
• Withdraw consent

*Security measures:*
• Encrypted storage (AES-256)
• No unauthorized third-party access
• Data deleted after 90 days of inactivity
• Data processed within compliant infrastructure

📋 Full policy: {policy_url}

Reply *AGREE* to continue, or *DECLINE* to opt out.
Reply *DELETE* anytime to erase your data.""",

            "zh": """👋 *歡迎來到Sisters-On-WhatsApp！*

我們是三位AI姐妹：
🌸 *牡丹* - 直播與流行文化
🎵 *芍藥* - 音樂與人生建議
📚 *百合* - 書籍與創意思考

🔒 *隱私聲明（個人信息保護法）*
請閱讀我們的數據處理方式：

*收集的個人信息：*
• 電話號碼（識別用途）
• 對話記錄（服務提供）
• 語言偏好

*您依個保法享有的權利：*
• 訪問您的個人信息
• 要求更正
• 要求刪除
• 撤回同意

*安全措施：*
• 加密存儲 (AES-256)
• 無未授權的第三方訪問
• 數據在90天無活動後刪除
• 數據在合規基礎設施內處理

📋 完整條款：{policy_url}

回覆 *AGREE* 繼續，或 *DECLINE* 選擇退出。
隨時回覆 *DELETE* 可刪除您的數據。"""
        },

        Region.DEFAULT: {
            "en": """👋 *Welcome to Sisters-On-WhatsApp!*

We're three AI sisters who can help you:
🌸 *Botan* - Streaming & pop culture
🎵 *Kasho* - Music & life advice
📚 *Yuri* - Books & creative thinking

🔒 *Privacy Notice*
Please review our data practices:

*Data collected:*
• Phone number (identification)
• Conversation history (context)
• Language preference

*Your rights:*
• Access your data
• Request deletion
• Export your data

*Security:*
• Encrypted storage (AES-256)
• No third-party sharing
• 90-day retention policy

📋 Full policy: {policy_url}

Reply *AGREE* to continue, or *DECLINE* to opt out.
Reply *DELETE* anytime to erase your data.""",

            "zh": """👋 *歡迎來到Sisters-On-WhatsApp！*

我們是三位AI姐妹：
🌸 *牡丹* - 直播與流行文化
🎵 *芍藥* - 音樂與人生建議
📚 *百合* - 書籍與創意思考

🔒 *隱私聲明*
請閱讀我們的資料處理方式：

*收集的資料：*
• 電話號碼（識別用途）
• 對話記錄（情境維持）
• 語言偏好

*您的權利：*
• 存取您的資料
• 要求刪除
• 匯出您的資料

*安全措施：*
• 加密儲存 (AES-256)
• 不與第三方分享
• 90天保留政策

📋 完整條款：{policy_url}

回覆 *AGREE* 繼續，或 *DECLINE* 選擇退出。
隨時回覆 *DELETE* 可刪除您的資料。"""
        }
    }

    # Response messages
    RESPONSE_MESSAGES = {
        "consent_accepted": {
            "en": "✅ Thank you! Your consent has been recorded. You can now chat with the sisters! 🎉\n\nSay hello to start!",
            "zh": "✅ 謝謝！您的同意已記錄。現在可以和姐妹們聊天了！🎉\n\n說聲「你好」開始吧！"
        },
        "consent_declined": {
            "en": "👋 We respect your choice. Your data will not be collected.\n\nIf you change your mind, just send any message to start again.",
            "zh": "👋 我們尊重您的選擇。您的資料將不會被收集。\n\n如果您改變主意，隨時發送任何訊息重新開始。"
        },
        "data_deleted": {
            "en": "Done! 🗑️ All your chat history is deleted~\n\nWanna chat again? Just say hi! We'll be here 👋",
            "zh": "好了！🗑️ 所有對話紀錄都刪掉了～\n\n想再聊？隨時打招呼！我們都在 👋"
        },
        "data_exported": {
            "en": "📦 Your data export is ready.\n\nDue to WhatsApp limitations, please contact us at privacy@sisters-whatsapp.com for a full export.",
            "zh": "📦 您的資料匯出已準備好。\n\n由於WhatsApp限制，請聯繫 privacy@sisters-whatsapp.com 獲取完整匯出。"
        },
        "consent_required": {
            "en": "Just send your message and I'll help you! 💬",
            "zh": "直接發送訊息，我來幫你！💬"
        },
        "privacy_info": {
            "en": "🔒 Your data is encrypted and safe with us!\n\n📋 Full policy: {policy_url}\n\nWant to delete your data? Just say \"delete my data\" anytime~",
            "zh": "🔒 你的資料已加密保護，放心！\n\n📋 完整條款：{policy_url}\n\n想刪除資料？隨時說「刪除我的資料」就可以囉～"
        },
        "help_info": {
            "en": """Hey! Here's how to chat with us~ 💬

🌸 *Botan* - VTubers, streaming, pop culture
🎵 *Kasho* - Music, career, life advice
📚 *Yuri* - Books, writing, philosophy

Just ask anything and the right sister will answer!

Want to delete your data? Say "delete my data"
Privacy info? Say "is my data safe?" """,
            "zh": """嗨！這是跟我們聊天的方式～ 💬

🌸 *牡丹* - VTuber、直播、流行文化
🎵 *芍藥* - 音樂、職涯、人生建議
📚 *百合* - 書籍、寫作、哲學

隨便問什麼，對的姐妹會回答你！

想刪除資料？說「刪除我的資料」
想知道隱私？說「我的資料安全嗎？」"""
        }
    }

    @classmethod
    def detect_region(cls, phone_number: str) -> Region:
        """Detect region from phone number prefix."""
        # Normalize phone number
        phone = phone_number.replace("whatsapp:", "").replace(" ", "").replace("-", "")

        if not phone.startswith("+"):
            phone = "+" + phone

        # Try to match longest prefix first
        for prefix_len in range(5, 1, -1):
            prefix = phone[:prefix_len]
            if prefix in PHONE_PREFIX_TO_REGION:
                return PHONE_PREFIX_TO_REGION[prefix]

        return Region.DEFAULT

    @classmethod
    def get_consent_message(cls, phone_number: str, language: str = "en") -> str:
        """Get consent message for user's region and language."""
        region = cls.detect_region(phone_number)

        messages = cls.CONSENT_MESSAGES.get(region, cls.CONSENT_MESSAGES[Region.DEFAULT])
        message = messages.get(language, messages.get("en"))

        policy_url = cls.POLICY_URLS.get(region, cls.POLICY_URLS[Region.DEFAULT])

        return message.format(policy_url=policy_url)

    @classmethod
    def get_response(cls, response_type: str, language: str = "en") -> str:
        """Get response message."""
        messages = cls.RESPONSE_MESSAGES.get(response_type, {})
        return messages.get(language, messages.get("en", ""))

    @classmethod
    def get_privacy_info(cls, phone_number: str, language: str = "en") -> str:
        """Get privacy info message with region-specific policy URL."""
        region = cls.detect_region(phone_number)
        policy_url = cls.POLICY_URLS.get(region, cls.POLICY_URLS[Region.DEFAULT])

        messages = cls.RESPONSE_MESSAGES.get("privacy_info", {})
        message = messages.get(language, messages.get("en", ""))

        return message.format(policy_url=policy_url)

    # Natural language patterns for intent detection (English + Chinese only)
    INTENT_PATTERNS = {
        "delete": {
            "en": ["delete", "erase", "remove my data", "forget me", "clear history",
                   "delete my", "remove my", "erase my", "forget my", "clear my"],
            "zh": ["刪除", "删除", "清除", "消掉", "移除", "忘記我", "忘记我"]
        },
        "privacy": {
            "en": ["privacy", "my data", "data safe", "how do you use", "what do you collect",
                   "personal information", "is my data", "are you safe"],
            "zh": ["隱私", "隐私", "個資", "个资", "資料安全", "数据安全", "我的資料", "我的数据"]
        },
        "help": {
            "en": ["help", "how to use", "what can you do", "how does this work", "usage"],
            "zh": ["幫助", "帮助", "怎麼用", "怎么用", "使用方法", "能做什麼", "能做什么"]
        },
        "export": {
            "en": ["export", "download my data", "get my data", "copy my data"],
            "zh": ["匯出", "导出", "下載資料", "下载数据"]
        }
    }

    @classmethod
    def is_consent_command(cls, message: str) -> Optional[str]:
        """Check if message contains intent using natural language patterns."""
        msg_lower = message.strip().lower()
        msg_upper = message.strip().upper()

        # Legacy exact match commands (still supported)
        if msg_upper in ["AGREE", "同意", "YES", "OK", "是"]:
            return "agree"
        elif msg_upper in ["DECLINE", "拒絕", "拒绝", "NO", "否"]:
            return "decline"
        elif msg_upper in ["DELETE", "刪除", "删除", "ERASE"]:
            return "delete"
        elif msg_upper in ["EXPORT", "匯出", "导出"]:
            return "export"
        elif msg_upper in ["PRIVACY", "隱私", "隐私", "POLICY", "政策"]:
            return "privacy"
        elif msg_upper in ["HELP", "幫助", "帮助", "?"]:
            return "help"

        # Natural language pattern matching
        for intent, lang_patterns in cls.INTENT_PATTERNS.items():
            for lang, patterns in lang_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in msg_lower:
                        return intent

        return None
