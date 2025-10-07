"""Provider package."""
from .base import VideoProvider, VideoRequest, VideoResponse, ProviderFeatures
from .sora import SoraProvider
from .runway import RunwayProvider
from .kling import KlingProvider


# Provider registry
PROVIDERS = {
    "openai": SoraProvider,
    "runway": RunwayProvider,
    "kling": KlingProvider,
}

# Model to provider mapping
MODEL_PROVIDER_MAP = {
    "sora-2": "openai",
    "sora-1": "openai",
    "runway-gen3": "runway",
    "runway-gen4": "runway",
    "kling-1.5": "kling",
    "kling-1.0": "kling",
}


def get_provider_for_model(model: str) -> str:
    """Get provider name for a model."""
    return MODEL_PROVIDER_MAP.get(model, "openai")


def create_provider(provider_name: str, api_key: str) -> VideoProvider:
    """Create provider instance."""
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_class(api_key)


__all__ = [
    "VideoProvider",
    "VideoRequest",
    "VideoResponse",
    "ProviderFeatures",
    "SoraProvider",
    "RunwayProvider",
    "KlingProvider",
    "PROVIDERS",
    "MODEL_PROVIDER_MAP",
    "get_provider_for_model",
    "create_provider",
]
