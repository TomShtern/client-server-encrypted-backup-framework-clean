# -*- coding: utf-8 -*-
"""
Font Configuration - Unicode and Emoji Support for KivyMD
Configures Kivy font registration for proper Hebrew and emoji rendering
"""

import os
from typing import Dict, List, Optional
from kivy.core.text import LabelBase
from kivy.logger import Logger


class UnicodeFont:
    """Configuration for a Unicode-capable font"""
    
    def __init__(self, name: str, regular: str, bold: Optional[str] = None, 
                 italic: Optional[str] = None, supports_emoji: bool = False,
                 supports_hebrew: bool = False):
        self.name = name
        self.regular = regular
        self.bold = bold
        self.italic = italic
        self.supports_emoji = supports_emoji
        self.supports_hebrew = supports_hebrew


class FontConfiguration:
    """Manages Unicode font registration for KivyMD"""
    
    # Define available Unicode fonts on Windows
    UNICODE_FONTS = {
        'SegoeUI': UnicodeFont(
            name='SegoeUI',
            regular='segoeui.ttf',
            bold='segoeuib.ttf', 
            italic='segoeuii.ttf',
            supports_emoji=False,  # Main text font
            supports_hebrew=True
        ),
        'SegoeUIEmoji': UnicodeFont(
            name='SegoeUIEmoji',
            regular='seguiemj.ttf',
            supports_emoji=True,
            supports_hebrew=False
        ),
        'SegoeUISymbol': UnicodeFont(
            name='SegoeUISymbol',
            regular='seguisym.ttf',
            supports_emoji=True,
            supports_hebrew=False
        ),
        'Arial': UnicodeFont(
            name='Arial',
            regular='arial.ttf',
            bold='arialbd.ttf',
            italic='ariali.ttf',
            supports_emoji=False,
            supports_hebrew=True
        )
    }
    
    _initialized = False
    _registered_fonts: Dict[str, bool] = {}
    
    @classmethod
    def initialize(cls) -> bool:
        """Initialize Unicode font support for KivyMD"""
        if cls._initialized:
            return True
            
        try:
            Logger.info("FontConfig: Initializing Unicode font support...")
            
            # Get system font directories
            font_dirs = LabelBase.get_system_fonts_dir()
            windows_fonts_dir = None
            
            # Find Windows fonts directory
            for font_dir in font_dirs:
                if 'WINDOWS' in font_dir.upper() and os.path.exists(font_dir):
                    windows_fonts_dir = font_dir
                    break
            
            if not windows_fonts_dir:
                Logger.warning("FontConfig: Windows fonts directory not found")
                return False
            
            Logger.info(f"FontConfig: Using fonts from {windows_fonts_dir}")
            
            # Register Unicode fonts
            registered_count = 0
            for font_config in cls.UNICODE_FONTS.values():
                if cls._register_font(font_config, windows_fonts_dir):
                    registered_count += 1
            
            Logger.info(f"FontConfig: Successfully registered {registered_count} Unicode font families")
            cls._initialized = True
            return True
            
        except Exception as e:
            Logger.error(f"FontConfig: Failed to initialize Unicode fonts: {e}")
            return False
    
    @classmethod
    def _register_font(cls, font_config: UnicodeFont, font_dir: str) -> bool:
        """Register a specific font family with Kivy"""
        try:
            # Check if regular font file exists
            regular_path = os.path.join(font_dir, font_config.regular)
            if not os.path.exists(regular_path):
                Logger.warning(f"FontConfig: Font file not found: {font_config.regular}")
                return False
            
            # Prepare font registration data using correct Kivy parameter names
            font_data = {
                'fn_regular': regular_path
            }
            
            # Add bold variant if available
            if font_config.bold:
                bold_path = os.path.join(font_dir, font_config.bold)
                if os.path.exists(bold_path):
                    font_data['fn_bold'] = bold_path
            
            # Add italic variant if available
            if font_config.italic:
                italic_path = os.path.join(font_dir, font_config.italic)
                if os.path.exists(italic_path):
                    font_data['fn_italic'] = italic_path
            
            # Register with Kivy
            LabelBase.register(name=font_config.name, **font_data)
            cls._registered_fonts[font_config.name] = True
            
            Logger.info(f"FontConfig: Registered font '{font_config.name}' with variants: {list(font_data.keys())}")
            return True
            
        except Exception as e:
            Logger.error(f"FontConfig: Failed to register font '{font_config.name}': {e}")
            return False
    
    @classmethod
    def get_best_font_for_content(cls, text: str) -> Optional[str]:
        """Get the best font name for specific text content"""
        if not cls._initialized:
            cls.initialize()
        
        try:
            # Check for emoji characters (Basic emoji detection)
            has_emoji = False
            has_hebrew = False
            
            for char in text:
                char_code = ord(char)
                
                # Check for emoji ranges
                if (0x1F600 <= char_code <= 0x1F64F or  # Emoticons
                    0x1F300 <= char_code <= 0x1F5FF or  # Symbols & Pictographs
                    0x1F680 <= char_code <= 0x1F6FF or  # Transport & Map
                    0x1F700 <= char_code <= 0x1F77F or  # Alchemical Symbols
                    0x1F780 <= char_code <= 0x1F7FF or  # Geometric Shapes Extended
                    0x1F800 <= char_code <= 0x1F8FF or  # Supplemental Arrows-C
                    0x2600 <= char_code <= 0x26FF or   # Miscellaneous Symbols
                    0x2700 <= char_code <= 0x27BF):    # Dingbats
                    has_emoji = True
                
                # Check for Hebrew characters
                if 0x0590 <= char_code <= 0x05FF:
                    has_hebrew = True
                
                # Early exit if we found both
                if has_emoji and has_hebrew:
                    break
            
            # Return best font based on content
            if has_emoji and cls._registered_fonts.get('SegoeUIEmoji', False):
                return 'SegoeUIEmoji'
            elif has_hebrew and cls._registered_fonts.get('SegoeUI', False):
                return 'SegoeUI'
            elif cls._registered_fonts.get('SegoeUI', False):
                return 'SegoeUI'  # Best overall Unicode font
            elif cls._registered_fonts.get('Arial', False):
                return 'Arial'  # Fallback Unicode font
            else:
                return None  # Use system default
                
        except Exception as e:
            Logger.warning(f"FontConfig: Error in font selection: {e}")
            return None
    
    @classmethod
    def get_emoji_font(cls) -> Optional[str]:
        """Get the best emoji font available"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._registered_fonts.get('SegoeUIEmoji', False):
            return 'SegoeUIEmoji'
        elif cls._registered_fonts.get('SegoeUISymbol', False):
            return 'SegoeUISymbol'
        else:
            return None
    
    @classmethod
    def get_hebrew_font(cls) -> Optional[str]:
        """Get the best Hebrew font available"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._registered_fonts.get('SegoeUI', False):
            return 'SegoeUI'
        elif cls._registered_fonts.get('Arial', False):
            return 'Arial'
        else:
            return None
    
    @classmethod
    def get_registered_fonts(cls) -> List[str]:
        """Get list of successfully registered font names"""
        return [name for name, registered in cls._registered_fonts.items() if registered]
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if font configuration is initialized"""
        return cls._initialized


# Convenience functions for easy usage
def initialize_unicode_fonts() -> bool:
    """Initialize Unicode font support - call this early in your app"""
    return FontConfiguration.initialize()

def get_font_for_text(text: str) -> Optional[str]:
    """Get the best font for specific text content"""
    return FontConfiguration.get_best_font_for_content(text)

def get_emoji_font() -> Optional[str]:
    """Get the best emoji font"""
    return FontConfiguration.get_emoji_font()

def get_hebrew_font() -> Optional[str]:
    """Get the best Hebrew font"""
    return FontConfiguration.get_hebrew_font()

def is_unicode_fonts_ready() -> bool:
    """Check if Unicode fonts are ready to use"""
    return FontConfiguration.is_initialized()

# Auto-initialize when imported (but catch any errors silently)
try:
    initialize_unicode_fonts()
except Exception:
    pass  # Will be retried when functions are called