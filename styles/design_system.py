"""
Modern Design System for Adaptive Study Planner
Production-ready color schemes, typography, and spacing
"""

class DesignSystem:
    
    # ==================== COLOR PALETTE ====================
    
    # Primary Colors (Blue/Purple Gradient)
    PRIMARY = "#6366F1"  # Indigo
    PRIMARY_DARK = "#4F46E5"
    PRIMARY_LIGHT = "#818CF8"
    
    # Secondary Colors
    SECONDARY = "#EC4899"  # Pink
    SECONDARY_DARK = "#DB2777"
    SECONDARY_LIGHT = "#F9A8D4"
    
    # Accent Colors
    ACCENT = "#10B981"  # Green (Success)
    ACCENT_WARNING = "#F59E0B"  # Amber
    ACCENT_ERROR = "#EF4444"  # Red
    
    # Neutral Colors
    BACKGROUND = "#0F172A"  # Dark Blue-Gray
    SURFACE = "#1E293B"
    SURFACE_LIGHT = "#334155"
    
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#CBD5E1"
    TEXT_MUTED = "#94A3B8"
    
    BORDER = "#475569"
    
    # Gradients
    GRADIENT_PRIMARY = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #10B981 0%, #059669 100%)"
    GRADIENT_WARNING = "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
    GRADIENT_CARD = "linear-gradient(135deg, #1E293B 0%, #0F172A 100%)"
    
    # ==================== TYPOGRAPHY ====================
    
    FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    FONT_FAMILY_MONO = "'Fira Code', 'Courier New', monospace"
    
    FONT_SIZE_XS = "0.75rem"   # 12px
    FONT_SIZE_SM = "0.875rem"  # 14px
    FONT_SIZE_BASE = "1rem"    # 16px
    FONT_SIZE_LG = "1.125rem"  # 18px
    FONT_SIZE_XL = "1.25rem"   # 20px
    FONT_SIZE_2XL = "1.5rem"   # 24px
    FONT_SIZE_3XL = "1.875rem" # 30px
    FONT_SIZE_4XL = "2.25rem"  # 36px
    
    # ==================== SPACING ====================
    
    SPACE_1 = "0.25rem"   # 4px
    SPACE_2 = "0.5rem"    # 8px
    SPACE_3 = "0.75rem"   # 12px
    SPACE_4 = "1rem"      # 16px
    SPACE_5 = "1.25rem"   # 20px
    SPACE_6 = "1.5rem"    # 24px
    SPACE_8 = "2rem"      # 32px
    SPACE_10 = "2.5rem"   # 40px
    SPACE_12 = "3rem"     # 48px
    
    # ==================== BORDER RADIUS ====================
    
    RADIUS_SM = "0.375rem"   # 6px
    RADIUS_MD = "0.5rem"     # 8px
    RADIUS_LG = "0.75rem"    # 12px
    RADIUS_XL = "1rem"       # 16px
    RADIUS_2XL = "1.5rem"    # 24px
    RADIUS_FULL = "9999px"
    
    # ==================== SHADOWS ====================
    
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    SHADOW_2XL = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
    
    SHADOW_GLOW = "0 0 20px rgba(99, 102, 241, 0.4)"
    
    # ==================== ANIMATION ====================
    
    TRANSITION_FAST = "150ms ease-in-out"
    TRANSITION_BASE = "300ms ease-in-out"
    TRANSITION_SLOW = "500ms ease-in-out"
    
    @staticmethod
    def get_status_color(status):
        """Get color based on status"""
        status_colors = {
            'completed': DesignSystem.ACCENT,
            'in_progress': DesignSystem.PRIMARY,
            'pending': DesignSystem.TEXT_MUTED,
            'failed': DesignSystem.ACCENT_ERROR
        }
        return status_colors.get(status, DesignSystem.TEXT_SECONDARY)
    
    @staticmethod
    def get_difficulty_color(difficulty):
        """Get color based on difficulty"""
        difficulty_colors = {
            'easy': DesignSystem.ACCENT,
            'medium': DesignSystem.ACCENT_WARNING,
            'hard': DesignSystem.ACCENT_ERROR
        }
        return difficulty_colors.get(difficulty.lower(), DesignSystem.TEXT_SECONDARY)
    
    @staticmethod
    def get_score_color(percentage):
        """Get color based on score percentage"""
        if percentage >= 80:
            return DesignSystem.ACCENT
        elif percentage >= 60:
            return DesignSystem.ACCENT_WARNING
        else:
            return DesignSystem.ACCENT_ERROR