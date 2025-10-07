"""Cost calculation service for different providers."""
from typing import Dict, Optional


class CostCalculator:
    """Calculate costs for video generation across providers."""

    # Pricing data for each provider (USD)
    PRICING = {
        "openai": {
            "sora-2": {
                "per_second": 0.10,  # $0.10 per second
                "base_cost": 0.0,
            },
            "sora-1": {
                "per_second": 0.10,
                "base_cost": 0.0,
            },
        },
        "runway": {
            "runway-gen3": {
                "per_second": 0.05,  # Approximate, Runway uses credits
                "base_cost": 0.0,
            },
            "runway-gen4": {
                "per_second": 0.075,  # Higher quality = higher cost
                "base_cost": 0.0,
            },
        },
        "kling": {
            "kling-1.5": {
                "per_second": 0.04,  # Approximate, Kling uses credits
                "base_cost": 0.0,
            },
            "kling-1.0": {
                "per_second": 0.03,
                "base_cost": 0.0,
            },
        },
    }

    @staticmethod
    def calculate_cost(
        provider: str,
        model: str,
        duration_seconds: float,
        resolution: Optional[str] = None,
    ) -> float:
        """Calculate the cost for a video generation.

        Args:
            provider: Provider name (openai, runway, kling)
            model: Model name (sora-2, runway-gen3, etc.)
            duration_seconds: Video duration in seconds
            resolution: Optional resolution (e.g., "1280x720")

        Returns:
            Estimated cost in USD
        """
        pricing = CostCalculator.PRICING.get(provider, {}).get(model)

        if not pricing:
            # Unknown provider/model, return 0
            return 0.0

        # Base cost
        total_cost = pricing["base_cost"]

        # Add per-second cost
        total_cost += pricing["per_second"] * duration_seconds

        # Resolution multiplier (if applicable)
        if resolution:
            multiplier = CostCalculator._get_resolution_multiplier(resolution)
            total_cost *= multiplier

        return round(total_cost, 4)

    @staticmethod
    def _get_resolution_multiplier(resolution: str) -> float:
        """Get cost multiplier based on resolution.

        Higher resolutions cost more.
        """
        if not resolution:
            return 1.0

        try:
            width, height = map(int, resolution.split("x"))
            total_pixels = width * height

            # Base: 1280x720 = 921,600 pixels
            base_pixels = 1280 * 720

            # Linear scaling based on pixel count
            multiplier = total_pixels / base_pixels
            return max(0.5, min(multiplier, 2.0))  # Clamp between 0.5x and 2x

        except:
            return 1.0

    @staticmethod
    def estimate_cost(
        provider: str,
        model: str,
        duration_seconds: float,
        aspect_ratio: Optional[str] = None,
    ) -> Dict[str, float]:
        """Estimate cost before generation.

        Args:
            provider: Provider name
            model: Model name
            duration_seconds: Planned duration
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1)

        Returns:
            Dictionary with cost breakdown
        """
        # Map aspect ratio to resolution
        resolution_map = {
            "16:9": "1280x720",
            "9:16": "720x1280",
            "1:1": "1024x1024",
        }
        resolution = resolution_map.get(aspect_ratio, "1280x720")

        cost = CostCalculator.calculate_cost(
            provider, model, duration_seconds, resolution
        )

        pricing = CostCalculator.PRICING.get(provider, {}).get(model, {})
        per_second_rate = pricing.get("per_second", 0.0)

        return {
            "estimated_cost": cost,
            "per_second_rate": per_second_rate,
            "duration": duration_seconds,
            "resolution": resolution,
            "breakdown": {
                "base": pricing.get("base_cost", 0.0),
                "duration_cost": per_second_rate * duration_seconds,
            },
        }

    @staticmethod
    def get_pricing_info() -> Dict[str, Dict]:
        """Get all pricing information.

        Returns:
            Complete pricing data for all providers
        """
        return CostCalculator.PRICING


# Singleton instance
_cost_calculator = None


def get_cost_calculator() -> CostCalculator:
    """Get cost calculator instance."""
    global _cost_calculator
    if _cost_calculator is None:
        _cost_calculator = CostCalculator()
    return _cost_calculator
