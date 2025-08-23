# -*- coding: utf-8 -*-
"""
MD3 Label Component - Unicode and Emoji Support for KivyMD
Ensures proper Hebrew and emoji rendering with automatic font selection
"""

from kivymd.uix.label import MDLabel
from kivy.logger import Logger
from kivy.metrics import dp
from typing import Optional


class MD3Label(MDLabel):
    """
    Material Design 3 Label with Unicode and emoji support
    
    This class automatically:
    - Prevents KivyMD vertical character stacking issues
    - Selects appropriate fonts for Hebrew and emoji content
    - Provides fallback font chain for Unicode characters
    """
    
    def __init__(self, **kwargs):
        # Import font configuration
        try:
            from kivymd_gui.utils.font_config import get_font_for_text, is_unicode_fonts_ready
            self._font_config_available = True
        except ImportError:
            Logger.warning("MD3Label: Font configuration not available - using system defaults")
            self._font_config_available = False
            get_font_for_text = None
            is_unicode_fonts_ready = lambda: False
        
        # Apply critical text rendering fixes before initialization
        kwargs.setdefault('markup', False)
        kwargs.setdefault('shorten', False)
        
        # CRITICAL: Configure Unicode font support
        original_text = kwargs.get('text', '')
        
        # Auto-select appropriate font based on text content
        if 'font_name' not in kwargs and self._font_config_available:
            if is_unicode_fonts_ready() and original_text:
                best_font = get_font_for_text(original_text)
                if best_font:
                    kwargs['font_name'] = best_font
                    Logger.debug(f"MD3Label: Selected font '{best_font}' for text content")
        
        # Initialize with corrected properties
        super().__init__(**kwargs)
        
        # Store font configuration state
        self._font_config_available = self._font_config_available
        
        # CRITICAL FIX: Override MDLabel's default text_size=(self.width, None) behavior
        # MDLabel automatically sets text_size to (self.width, None) which causes character-by-character
        # vertical text rendering when the width is small. We need to explicitly set it to (None, None)
        # to allow proper horizontal text rendering.
        if 'text_size' not in kwargs:  # Only override if not explicitly set
            self.text_size = (None, None)
            # Also schedule a delayed fix for cases where the parent container resets text_size
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self, 'text_size', (None, None)), 0.1)
        
        # Enhanced protection against vertical text rendering
        self._apply_text_rendering_protection()
        
        # Bind to events to maintain fix
        self.bind(parent=self._on_parent_change)
        self.bind(size=self._on_size_change)
        
        # Ensure other properties are properly set after initialization
        self.markup = False
        self.shorten = False
    
    def _apply_text_rendering_protection(self):
        """Apply comprehensive text rendering protection"""
        # CRITICAL: Always use (None, None) for text_size to prevent vertical character stacking
        # Using width-based text_size can cause text overlapping issues
        self.text_size = (None, None)
        
        # Ensure minimum width for proper text rendering
        if hasattr(self, 'width') and self.width < dp(100):
            self.size_hint_x = None
            self.width = dp(120)  # Increased minimum width
        
        # Ensure proper text alignment
        if not hasattr(self, 'halign') or not self.halign:
            self.halign = 'left'
        
        # Enable adaptive height to prevent text overlapping
        self.adaptive_height = True
        
        # Add padding for better text spacing
        if not hasattr(self, 'padding') or not self.padding:
            self.padding = [dp(4), dp(2), dp(4), dp(2)]
    
    def _on_parent_change(self, instance, parent):
        """Handle parent changes to maintain text rendering protection"""
        if parent:
            # Re-apply protection when parent changes
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._apply_text_rendering_protection(), 0.01)
    
    def _on_size_change(self, instance, size):
        """Handle size changes to maintain text rendering protection"""
        # CRITICAL: Always maintain (None, None) for text_size to prevent overlapping
        self.text_size = (None, None)
        
        # Ensure minimum width for proper text rendering
        if size[0] < dp(100):  # Increased minimum width threshold
            self.size_hint_x = None
            self.width = dp(120)  # Increased minimum width
        
        # Ensure adaptive height to prevent text overlapping
        self.adaptive_height = True
    
    def on_text(self, instance, text):
        """Handle text changes to automatically select appropriate font"""
        # Auto-update font if content changes and no explicit font was set
        if (self._font_config_available and hasattr(self, '_auto_font_selection') and 
            getattr(self, '_auto_font_selection', True)):
            
            try:
                from kivymd_gui.utils.font_config import get_font_for_text, is_unicode_fonts_ready
                
                if is_unicode_fonts_ready() and text:
                    best_font = get_font_for_text(text)
                    if best_font and best_font != self.font_name:
                        self.font_name = best_font
                        Logger.debug(f"MD3Label: Auto-updated font to '{best_font}' for new text content")
            except ImportError:
                pass


def create_md3_label(text="", **kwargs):
    """
    Factory function to create MD3-compliant labels with Unicode support
    
    Args:
        text: The text to display (supports Hebrew and emoji)
        **kwargs: Additional MDLabel properties
        
    Returns:
        MD3Label: Properly configured label widget with Unicode font selection
    """
    kwargs['text'] = text
    return MD3Label(**kwargs)


def create_unicode_label(text="", force_unicode_font=True, **kwargs):
    """
    Factory function specifically for Unicode text (Hebrew, emoji, etc.)
    
    Args:
        text: The Unicode text to display
        force_unicode_font: Force selection of Unicode-capable font
        **kwargs: Additional MDLabel properties
        
    Returns:
        MD3Label: Label optimized for Unicode content
    """
    # Force Unicode font selection if requested
    if force_unicode_font:
        try:
            from kivymd_gui.utils.font_config import get_font_for_text, get_emoji_font, get_hebrew_font
            
            # Try to get the best font for the content
            if text:
                best_font = get_font_for_text(text)
                if best_font:
                    kwargs['font_name'] = best_font
            # Fallback to emoji font if no specific font found but text has emojis
            elif any(ord(char) > 127 for char in text if ord(char) >= 0x1F600):
                emoji_font = get_emoji_font()
                if emoji_font:
                    kwargs['font_name'] = emoji_font
                    
        except ImportError:
            Logger.warning("Unicode font configuration not available")
    
    kwargs['text'] = text
    return MD3Label(**kwargs)


# Convenience functions for common label types with Unicode support
def create_title_label(text, **kwargs):
    """Create a title-style label with Unicode support"""
    kwargs.update({
        'font_style': 'Title',
        'theme_text_color': 'Primary',
        'halign': 'left'
    })
    return create_md3_label(text, **kwargs)


def create_body_label(text, **kwargs):
    """Create a body-style label with Unicode support"""
    kwargs.update({
        'font_style': 'Body',
        'theme_text_color': 'Primary',
        'halign': 'left'
    })
    return create_md3_label(text, **kwargs)


def create_caption_label(text, **kwargs):
    """Create a caption-style label with Unicode support"""
    kwargs.update({
        'font_style': 'Label',
        'theme_text_color': 'Secondary',
        'halign': 'left'
    })
    return create_md3_label(text, **kwargs)


def create_emoji_label(text, **kwargs):
    """Create a label optimized for emoji content"""
    try:
        from kivymd_gui.utils.font_config import get_emoji_font
        emoji_font = get_emoji_font()
        if emoji_font:
            kwargs['font_name'] = emoji_font
    except ImportError:
        pass
    
    kwargs['text'] = text
    return MD3Label(**kwargs)


def create_hebrew_label(text, **kwargs):
    """Create a label optimized for Hebrew content"""
    try:
        from kivymd_gui.utils.font_config import get_hebrew_font
        hebrew_font = get_hebrew_font()
        if hebrew_font:
            kwargs['font_name'] = hebrew_font
    except ImportError:
        pass
    
    kwargs['text'] = text
    return MD3Label(**kwargs)