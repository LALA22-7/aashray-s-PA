"""
Domain enumerations for account management and automation.
"""

from enum import Enum


class PlatformType(str, Enum):
    """Supported social media platforms."""
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"


class AccountType(str, Enum):
    """Account identity classification."""
    PERSONAL = "personal"
    BUSINESS = "business"


class IntegrationType(str, Enum):
    """Integration mechanism."""
    MANUAL = "manual"
    WHATSAPP_CLOUD_API = "whatsapp_cloud_api"
    INSTAGRAM_MESSAGING_API = "instagram_messaging_api"


class IntegrationStatus(str, Enum):
    """Operational status of the account integration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class AutomationMode(str, Enum):
    """Automation execution policy."""
    AUTOMATIC = "automatic"
    APPROVAL = "approval"
    DISABLED = "disabled"


class ReplyLength(str, Enum):
    """Expected response length."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

