"""
GreenCode Sentinel - UI Styling Constants
Professional color scheme and styling for the dashboard.
"""

import flet as ft

# Color Palette - Professional Green Theme
class Colors:
    """Color constants for the application."""
    PRIMARY = "#2E7D32"          # Dark Green
    PRIMARY_LIGHT = "#4CAF50"    # Light Green
    PRIMARY_DARK = "#1B5E20"     # Darker Green
    
    SECONDARY = "#00897B"        # Teal
    SECONDARY_LIGHT = "#26A69A"  # Light Teal
    
    ACCENT = "#FFC107"           # Amber (for warnings)
    ERROR = "#D32F2F"            # Red
    SUCCESS = "#388E3C"          # Green
    WARNING = "#F57C00"          # Orange
    INFO = "#1976D2"             # Blue
    
    BACKGROUND = "#FAFAFA"       # Light Gray
    SURFACE = "#FFFFFF"          # White
    TEXT_PRIMARY = "#212121"     # Dark Gray
    TEXT_SECONDARY = "#757575"   # Medium Gray
    DIVIDER = "#BDBDBD"          # Light Gray
    
    # Grade Colors
    GRADE_A = "#4CAF50"          # Green
    GRADE_B = "#8BC34A"          # Light Green
    GRADE_C = "#FFC107"          # Amber
    GRADE_D = "#FF9800"          # Orange
    GRADE_F = "#F44336"          # Red


# Typography
class Typography:
    """Typography constants."""
    TITLE_SIZE = 32
    SUBTITLE_SIZE = 24
    HEADING_SIZE = 20
    BODY_SIZE = 16
    CAPTION_SIZE = 14
    SMALL_SIZE = 12
    
    FONT_FAMILY = "Segoe UI"


# Spacing
class Spacing:
    """Spacing constants."""
    XS = 4
    SM = 8
    MD = 16
    LG = 24
    XL = 32
    XXL = 48


# Border Radius
class BorderRadius:
    """Border radius constants."""
    SM = 4
    MD = 8
    LG = 12
    XL = 16
    ROUND = 50


# Shadows
class Shadows:
    """Shadow elevation constants."""
    NONE = 0
    SM = 2
    MD = 4
    LG = 8
    XL = 16


def get_grade_color(grade: str) -> str:
    """
    Get color for a grade.
    
    Args:
        grade: Letter grade (A+, A, B, C, D, F)
        
    Returns:
        Hex color code
    """
    if grade in ["A+", "A", "A-"]:
        return Colors.GRADE_A
    elif grade in ["B+", "B", "B-"]:
        return Colors.GRADE_B
    elif grade in ["C+", "C", "C-"]:
        return Colors.GRADE_C
    elif grade == "D":
        return Colors.GRADE_D
    else:
        return Colors.GRADE_F


def get_score_color(score: float) -> str:
    """
    Get color based on score value.
    
    Args:
        score: Sustainability score (0-100)
        
    Returns:
        Hex color code
    """
    if score >= 90:
        return Colors.GRADE_A
    elif score >= 75:
        return Colors.GRADE_B
    elif score >= 60:
        return Colors.GRADE_C
    elif score >= 50:
        return Colors.GRADE_D
    else:
        return Colors.GRADE_F


def create_button_style(
    bgcolor: str = Colors.PRIMARY,
    color: str = Colors.SURFACE,
    elevation: int = Shadows.MD
) -> dict:
    """
    Create a button style dictionary.
    
    Args:
        bgcolor: Background color
        color: Text color
        elevation: Shadow elevation
        
    Returns:
        Style dictionary
    """
    return {
        "bgcolor": bgcolor,
        "color": color,
        "elevation": elevation,
        "style": ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.MD),
        )
    }


def create_card_style(elevation: int = Shadows.SM) -> dict:
    """
    Create a card container style.
    
    Args:
        elevation: Shadow elevation
        
    Returns:
        Style dictionary
    """
    return {
        "bgcolor": Colors.SURFACE,
        "border_radius": BorderRadius.LG,
        "padding": Spacing.LG,
        "shadow": ft.BoxShadow(
            spread_radius=1,
            blur_radius=elevation,
            color=Colors.TEXT_PRIMARY,
            offset=ft.Offset(0, 2),
        )
    }

# Made with Bob
