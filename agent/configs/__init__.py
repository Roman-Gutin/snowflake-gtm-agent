"""
Agent Configs Module

Import agent configurations.
"""

from . import gtm_engineer

# Registry of available agent configs
CONFIG_REGISTRY = {
    "gtm_engineer": gtm_engineer,
}

def get_config(config_name: str):
    """Get an agent configuration by name."""
    if config_name in CONFIG_REGISTRY:
        return CONFIG_REGISTRY[config_name]
    else:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(CONFIG_REGISTRY.keys())}")

