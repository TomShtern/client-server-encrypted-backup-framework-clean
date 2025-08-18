# -*- coding: utf-8 -*-
"""
asset_manager.py - A robust, caching asset loader for the Server GUI.

This module provides a centralized `AssetManager` class to handle the loading,
resizing, and caching of all UI assets, including icons, images, and sounds.

Key Features:
- **Centralized Management:** A single source for all asset-related operations.
- **Performance:** Caches loaded assets in memory to prevent redundant disk I/O.
- **Robustness:** Gracefully handles missing assets by generating and caching a
  placeholder, preventing the UI from crashing and clearly indicating the issue.
- **Dynamic Resizing:** Icons can be requested at any size, and the manager will
  handle high-quality resampling on the fly.
- **Garbage Collection Safety:** Correctly manages `tk.PhotoImage` references to
  prevent them from being garbage collected and disappearing from the UI.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class AssetManager:
    """A class that manages loading and caching of GUI assets."""

    def __init__(self):
        """Initializes the AssetManager and locates the asset base directory."""
        self.ASSETS_DIR = Path(__file__).parent.resolve()
        
        # Caches to prevent re-loading and re-processing files from disk.
        self._icon_cache: Dict[str, ImageTk.PhotoImage] = {}
        self._image_cache: Dict[str, Image.Image] = {}
        self._sound_cache: Dict[str, str] = {}
        
        # A critical reference store to prevent Tkinter's garbage collection
        # from deleting PhotoImage objects that are in use.
        self._photo_image_references: Dict[str, ImageTk.PhotoImage] = {}
        print(f"[OK]   AssetManager initialized. Asset directory: {self.ASSETS_DIR}")

    def get_sound(self, name: str) -> Optional[str]:
        """
        Gets the full path to a sound file.

        Args:
            name (str): The name of the sound file (e.g., 'success.wav').

        Returns:
            Optional[str]: The absolute path to the sound file, or None if not found.
        """
        if name in self._sound_cache:
            return self._sound_cache[name]

        sound_path = self.ASSETS_DIR / "sounds" / name
        if sound_path.exists():
            path_str = str(sound_path)
            self._sound_cache[name] = path_str
            return path_str
        else:
            print(f"[WARNING] Sound asset not found: {name}")
            return None

    def get_image(self, name: str) -> Optional[Image.Image]:
        """
        Loads a PIL Image from the 'images' directory. Caches the result.

        Args:
            name (str): The name of the image file (e.g., 'logo.png').

        Returns:
            Optional[Image.Image]: The loaded PIL Image object, or None if not found.
        """
        if name in self._image_cache:
            return self._image_cache[name]

        image_path = self.ASSETS_DIR / "images" / name
        if image_path.exists():
            try:
                image = Image.open(image_path)
                self._image_cache[name] = image
                return image
            except Exception as e:
                print(f"[ERROR] Failed to load image asset '{name}': {e}")
                return None
        else:
            print(f"[WARNING] Image asset not found: {name}")
            return None

    def get_icon(self, name: str, size: Tuple[int, int] = (16, 16)) -> ImageTk.PhotoImage:
        """
        Loads, resizes, and returns a ImageTk.PhotoImage from an icon file.
        
        This method is the workhorse for all icons in the UI. It dynamically
        resizes icons to the requested dimensions and caches the result for
        high performance. If an icon is not found, it generates a visible
        placeholder instead of crashing.

        Args:
            name (str): The name of the icon file (e.g., 'house-door-fill.png').
            size (Tuple[int, int]): The desired (width, height) for the icon.

        Returns:
            ImageTk.PhotoImage: The processed, ready-to-use Tkinter PhotoImage.
        """
        cache_key = f"{name}_{size[0]}x{size[1]}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        icon_path = self.ASSETS_DIR / "icons" / f"{name}.png"
        
        try:
            if not icon_path.exists():
                raise FileNotFoundError(f"Icon asset not found: {icon_path}")

            with Image.open(icon_path) as img:
                # Use high-quality resizing
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_img)
        
        except Exception as e:
            print(f"[WARNING] {e}. Creating placeholder for icon '{name}'.")
            photo_image = self._create_placeholder_icon(size)

        # Store in cache AND in the critical reference holder.
        self._icon_cache[cache_key] = photo_image
        self._photo_image_references[cache_key] = photo_image
        
        return photo_image

    def _create_placeholder_icon(self, size: Tuple[int, int]) -> ImageTk.PhotoImage:
        """
        Generates a visible magenta placeholder icon.
        This is a resilience feature to prevent crashes on missing assets.
        """
        cache_key = f"placeholder_{size[0]}x{size[1]}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        img = Image.new('RGB', size, 'magenta')
        photo_image = ImageTk.PhotoImage(img)
        
        self._icon_cache[cache_key] = photo_image
        self._photo_image_references[cache_key] = photo_image
        
        return photo_image