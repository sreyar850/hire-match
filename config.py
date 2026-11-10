"""
Configuration and constants for HireMatch AI.
"""

from typing import Dict

# Default weights for composite matching score
DEFAULT_WEIGHTS: Dict[str, float] = {
    "skills": 0.45,
    "semantic": 0.25,
    "experience": 0.20,
    "education": 0.10,
}

# Degree level hierarchy for scoring
EDUCATION_LEVELS: Dict[str, int] = {
    "phd": 4,
    "doctorate": 4,
    "master": 3,
    "m.tech": 3,
    "m.s": 3,
    "ms": 3,
    "mba": 3,
    "mca": 3,
    "bachelor": 2,
    "b.tech": 2,
    "b.e": 2,
    "b.s": 2,
    "bs": 2,
    "bca": 2,
    "bba": 2,
    "associate": 1,
    "diploma": 1,
    "high school": 0,
    "none": 0,
}

# Match category tier thresholds (percentage 0-100)
TIER_THRESHOLDS = {
    "strong": 75.0,
    "moderate": 55.0,
    "low": 0.0,
}

# Tier styling and labels
TIER_INFO = {
    "strong": {
        "label": "Top Match",
        "badge_color": "#10B981",  # Emerald Green
        "icon": "🌟",
        "description": "Exceeds or closely meets all core requirements.",
    },
    "moderate": {
        "label": "Potential Fit",
        "badge_color": "#F59E0B",  # Amber Orange
        "icon": "⚡",
        "description": "Meets most criteria; may have minor skill or experience gaps.",
    },
    "low": {
        "label": "Low Alignment",
        "badge_color": "#EF4444",  # Red
        "icon": "⚠️",
        "description": "Significant gaps in required skills or qualifications.",
    },
}

# Application UI theme colors
THEME_COLORS = {
    "primary": "#4F46E5",     # Indigo
    "secondary": "#06B6D4",   # Cyan
    "accent": "#8B5CF6",      # Purple
    "success": "#10B981",     # Emerald
    "warning": "#F59E0B",     # Amber
    "danger": "#EF4444",      # Rose
    "card_bg": "#FFFFFF",
    "text_dark": "#1E293B",
}
