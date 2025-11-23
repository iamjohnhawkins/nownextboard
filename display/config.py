"""Configuration for the display application."""

# Display settings for HyperPixel 4
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FULLSCREEN = False  # Set to True for production on Pi

# API settings
API_URL = "http://localhost:5001"
POLL_INTERVAL = 5  # Seconds between API polls

# Colors
BG_COLOR = (240, 240, 245)
TEXT_COLOR = (40, 40, 50)
TEXT_LIGHT_COLOR = (100, 100, 120)
BORDER_COLOR = (200, 200, 210)

# Timer ring settings
RING_THICKNESS = 20
RING_REMAINING_COLOR = (76, 175, 80)  # Green
RING_ELAPSED_COLOR = (220, 220, 230)  # Light gray

# Fonts (will be loaded in main.py)
FONT_SIZE_LARGE = 72
FONT_SIZE_MEDIUM = 48
FONT_SIZE_SMALL = 32
FONT_SIZE_LABEL = 24

# Layout
PADDING = 40
CARD_PADDING = 30
