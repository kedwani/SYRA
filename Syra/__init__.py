"""SYRA - Medical Identification Platform for Egypt."""

default_app_config = "syra.apps.SyraConfig"

# Validate configuration on startup
try:
    from .config_validator import validate_configuration

    validate_configuration()
except ImportError:
    # During initial setup, config_validator may not exist yet
    pass
