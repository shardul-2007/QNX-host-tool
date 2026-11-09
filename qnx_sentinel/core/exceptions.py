"""
QNX Sentinel - Custom Exceptions
"""

class QNXSentinelError(Exception):
    """Base exception for all QNX Sentinel errors."""
    pass

class SDKNotFoundError(QNXSentinelError):
    """Raised when QNX SDP 8.0 environment is required but missing."""
    pass

class InvalidProjectError(QNXSentinelError):
    """Raised when the specified target directory is invalid or empty."""
    pass

class BuildAssistantError(QNXSentinelError):
    """Raised during build configuration generation or validation."""
    pass

class TargetExecutionError(QNXSentinelError):
    """Raised when target execution or test runner fails."""
    pass
