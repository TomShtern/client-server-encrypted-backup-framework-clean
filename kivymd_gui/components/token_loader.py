"""
Material Design 3 Token Loader and Utilities
Centralized token loading and color conversion utilities for M3 compliance
"""

import json
import os
from typing import Dict, Any, Union, Tuple


class TokenLoader:
    """Centralized token loader for Material Design 3 design tokens"""
    
    _instance = None
    _tokens = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._tokens is None:
            self.load_tokens()
    
    def load_tokens(self) -> Dict[str, Any]:
        """Load design tokens from tokens.json"""
        tokens_path = os.path.join(os.path.dirname(__file__), '..', 'tokens.json')
        try:
            with open(tokens_path, 'r') as f:
                self._tokens = json.load(f)
            print(f"[INFO] Loaded M3 design tokens v{self._tokens.get('version', 'unknown')}")
            return self._tokens
        except FileNotFoundError:
            print(f"[ERROR] tokens.json not found at {tokens_path}")
            return self._get_fallback_tokens()
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in tokens.json: {e}")
            return self._get_fallback_tokens()
    
    def _get_fallback_tokens(self) -> Dict[str, Any]:
        """Fallback tokens if tokens.json is unavailable"""
        return {
            "palette": {"primary": "#1976D2"},
            "shape": {"corner_medium": 12},
            "elevation": {"level1": 1},
            "motion": {"standard": 250},
            "spacing": {"grid": 8}
        }
    
    @property
    def tokens(self) -> Dict[str, Any]:
        """Get loaded tokens"""
        return self._tokens or self.load_tokens()


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
    """Convert hex color to RGBA tuple for KivyMD"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b, alpha)
    except (ValueError, IndexError):
        # Fallback to blue if conversion fails
        return (0.098, 0.463, 0.824, alpha)


def get_token_value(token_path: str, fallback: Any = None) -> Any:
    """
    Get a token value using dot notation (e.g. 'palette.primary' or 'shape.corner_medium')
    
    Args:
        token_path: Dot-separated path to token (e.g. 'palette.primary')
        fallback: Fallback value if token not found
        
    Returns:
        Token value or fallback
    """
    loader = TokenLoader()
    tokens = loader.tokens
    
    try:
        keys = token_path.split('.')
        value = tokens
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        if fallback is not None:
            return fallback
        print(f"[WARNING] Token '{token_path}' not found, using fallback")
        return fallback


def apply_responsive_tokens(component: Any, base_tokens: Dict[str, Any], 
                          screen_width: float) -> None:
    """
    Apply responsive token adjustments based on screen width
    
    Args:
        component: KivyMD component to modify
        base_tokens: Base token values
        screen_width: Current screen width in dp
    """
    breakpoints = get_token_value('breakpoints', {
        'mobile': 600, 'tablet': 905, 'desktop': 1240
    })
    
    if screen_width <= breakpoints['mobile']:
        # Mobile adjustments - larger touch targets, bigger radii
        scale_factor = 1.33
    elif screen_width <= breakpoints['tablet']:
        # Tablet adjustments - moderate scaling
        scale_factor = 1.17
    else:
        # Desktop - standard tokens
        scale_factor = 1.0
    
    # Apply scaling to radius if component has it
    if hasattr(component, 'radius') and 'radius' in base_tokens:
        base_radius = base_tokens['radius']
        component.radius = [base_radius * scale_factor]
    
    # Apply scaling to padding if component has it
    if hasattr(component, 'padding') and 'padding' in base_tokens:
        base_padding = base_tokens['padding']
        if isinstance(base_padding, (list, tuple)):
            component.padding = [p * scale_factor for p in base_padding]
        else:
            component.padding = base_padding * scale_factor


# Singleton instance
token_loader = TokenLoader()