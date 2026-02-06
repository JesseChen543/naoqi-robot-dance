# -*- coding: utf-8 -*-
"""
Utilities for Pepper Robot dance system.

Includes animation discovery and listing tools.
"""

from .animations import (
    fetch_animation_paths,
    fetch_animation_tags,
    fetch_tag_map,
    build_animation_catalog,
    categorize_paths,
)

__all__ = [
    'fetch_animation_paths',
    'fetch_animation_tags',
    'fetch_tag_map',
    'build_animation_catalog',
    'categorize_paths',
]
