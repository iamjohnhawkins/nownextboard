"""Rendering logic for the Now-Next board display."""
import pygame
import math
import os
import urllib.request
from typing import Optional, Dict, Any
from config import *


class Renderer:
    """Handles all rendering for the display."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        # Load fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_label = pygame.font.Font(None, FONT_SIZE_LABEL)

        # Cache for loaded background images
        self.image_cache = {}

    def get_timer_color(self, progress_percent: float) -> tuple:
        """
        Calculate timer color based on progress.
        Green (0-50%) -> Amber (50-75%) -> Red (75-100%)
        """
        if progress_percent < 50:
            # Green to Amber transition (0-50%)
            ratio = progress_percent / 50.0
            r = int(TIMER_COLOR_GREEN[0] + (TIMER_COLOR_AMBER[0] - TIMER_COLOR_GREEN[0]) * ratio)
            g = int(TIMER_COLOR_GREEN[1] + (TIMER_COLOR_AMBER[1] - TIMER_COLOR_GREEN[1]) * ratio)
            b = int(TIMER_COLOR_GREEN[2] + (TIMER_COLOR_AMBER[2] - TIMER_COLOR_GREEN[2]) * ratio)
        elif progress_percent < 75:
            # Amber to Red transition (50-75%)
            ratio = (progress_percent - 50) / 25.0
            r = int(TIMER_COLOR_AMBER[0] + (TIMER_COLOR_RED[0] - TIMER_COLOR_AMBER[0]) * ratio)
            g = int(TIMER_COLOR_AMBER[1] + (TIMER_COLOR_RED[1] - TIMER_COLOR_AMBER[1]) * ratio)
            b = int(TIMER_COLOR_AMBER[2] + (TIMER_COLOR_RED[2] - TIMER_COLOR_AMBER[2]) * ratio)
        else:
            # Pure red (75-100%)
            r, g, b = TIMER_COLOR_RED

        return (r, g, b)

    def draw_border_timer(self, progress_percent: float):
        """Draw a rectangular border timer around the screen edge."""
        thickness = RING_THICKNESS

        # Draw background border (elapsed portion)
        pygame.draw.rect(self.screen, RING_ELAPSED_COLOR,
                        (0, 0, self.width, self.height), thickness)

        if progress_percent <= 0:
            return

        # Calculate color based on progress
        timer_color = self.get_timer_color(progress_percent)

        # Calculate total perimeter
        perimeter = 2 * (self.width + self.height)
        progress_distance = (progress_percent / 100) * perimeter

        # Draw progress border starting from top-center going clockwise
        points = []

        # Start at top center
        start_x = self.width // 2
        start_y = 0
        current_distance = 0

        # Top edge - right half (top-center to top-right)
        top_right_distance = self.width // 2
        if progress_distance > current_distance:
            end_x = min(start_x + (progress_distance - current_distance), self.width)
            pygame.draw.line(self.screen, timer_color,
                           (start_x, thickness // 2), (end_x, thickness // 2), thickness)
        current_distance += top_right_distance

        if progress_distance <= current_distance:
            return

        # Right edge (top to bottom)
        right_edge_distance = self.height
        if progress_distance > current_distance:
            end_y = min(progress_distance - current_distance, self.height)
            pygame.draw.line(self.screen, timer_color,
                           (self.width - thickness // 2, 0),
                           (self.width - thickness // 2, end_y), thickness)
        current_distance += right_edge_distance

        if progress_distance <= current_distance:
            return

        # Bottom edge (right to left)
        bottom_edge_distance = self.width
        if progress_distance > current_distance:
            end_x = max(self.width - (progress_distance - current_distance), 0)
            pygame.draw.line(self.screen, timer_color,
                           (self.width, self.height - thickness // 2),
                           (end_x, self.height - thickness // 2), thickness)
        current_distance += bottom_edge_distance

        if progress_distance <= current_distance:
            return

        # Left edge (bottom to top)
        left_edge_distance = self.height
        if progress_distance > current_distance:
            end_y = max(self.height - (progress_distance - current_distance), 0)
            pygame.draw.line(self.screen, timer_color,
                           (thickness // 2, self.height),
                           (thickness // 2, end_y), thickness)
        current_distance += left_edge_distance

        if progress_distance <= current_distance:
            return

        # Top edge - left half (top-left to top-center)
        if progress_distance > current_distance:
            end_x = min(progress_distance - current_distance, self.width // 2)
            pygame.draw.line(self.screen, timer_color,
                           (0, thickness // 2), (end_x, thickness // 2), thickness)

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list:
        """Wrap text to fit within a given width."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Try adding this word to the current line
            test_line = ' '.join(current_line + [word])
            test_surf = font.render(test_line, True, TEXT_COLOR)

            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                # Line is too long, start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def get_image_keywords(self, activity_name: str) -> str:
        """Extract keywords from activity name for image search."""
        activity_lower = activity_name.lower()

        # Keyword mapping for common activities
        keyword_map = {
            'wake': 'sunrise morning calm',
            'dress': 'clothes wardrobe peaceful',
            'breakfast': 'healthy breakfast light',
            'lunch': 'healthy lunch food',
            'dinner': 'healthy dinner food',
            'eat': 'healthy food calm',
            'brush': 'bathroom peaceful clean',
            'teeth': 'bathroom peaceful clean',
            'bath': 'bathroom spa peaceful',
            'shower': 'bathroom spa water',
            'school': 'books learning peaceful',
            'homework': 'desk study calm',
            'read': 'book reading calm',
            'play': 'play outdoor nature',
            'outside': 'nature outdoor peaceful',
            'park': 'nature park peaceful',
            'bed': 'bedroom sleep peaceful',
            'sleep': 'bedroom sleep calm',
            'pack': 'organize tidy peaceful',
            'clean': 'organized tidy peaceful',
            'shoes': 'shoes organized peaceful',
            'jacket': 'coat organized peaceful',
            'snack': 'healthy snack food',
            'exercise': 'exercise yoga peaceful',
            'walk': 'walking nature peaceful',
            'leave': 'door pathway calm',
        }

        # Find matching keywords
        for key, keywords in keyword_map.items():
            if key in activity_lower:
                return keywords

        # Default to peaceful/calm imagery
        return 'calm peaceful nature'

    def get_auto_background_color(self, activity_name: str) -> tuple:
        """Get a calming background color based on activity type."""
        activity_lower = activity_name.lower()

        # Color mapping for different activity types (soft, calming colors)
        color_map = {
            'wake': (255, 248, 220),      # Cornsilk - soft morning yellow
            'dress': (230, 230, 250),     # Lavender - calm purple
            'breakfast': (255, 250, 205), # Lemon chiffon - light yellow
            'lunch': (255, 239, 213),     # Papaya whip - warm orange
            'dinner': (255, 228, 196),    # Bisque - warm peach
            'eat': (255, 245, 238),       # Seashell - soft pink
            'brush': (224, 255, 255),     # Light cyan - water blue
            'teeth': (224, 255, 255),     # Light cyan - water blue
            'bath': (240, 248, 255),      # Alice blue - water blue
            'shower': (240, 248, 255),    # Alice blue - water blue
            'school': (255, 250, 240),    # Floral white - paper white
            'homework': (245, 245, 220),  # Beige - calm tan
            'read': (250, 240, 230),      # Linen - book pages
            'play': (240, 255, 240),      # Honeydew - fresh green
            'outside': (240, 255, 255),   # Azure - sky blue
            'park': (245, 255, 250),      # Mint cream - nature green
            'bed': (230, 230, 250),       # Lavender - evening calm
            'sleep': (230, 230, 250),     # Lavender - evening calm
            'pack': (255, 250, 250),      # Snow - organized white
            'clean': (245, 255, 250),     # Mint cream - fresh clean
            'shoes': (250, 235, 215),     # Antique white - neutral
            'jacket': (255, 248, 220),    # Cornsilk - warm tan
            'snack': (255, 245, 238),     # Seashell - light peach
            'exercise': (240, 255, 240),  # Honeydew - active green
            'walk': (245, 255, 250),      # Mint cream - nature
            'leave': (255, 250, 205),     # Lemon chiffon - bright start
        }

        # Find matching color
        for key, color in color_map.items():
            if key in activity_lower:
                return color

        # Default to soft white/cream
        return (250, 250, 245)

    def create_gradient_background(self, width: int, height: int, color: tuple) -> pygame.Surface:
        """Create a subtle gradient background with the given base color."""
        surface = pygame.Surface((width, height))

        # Create a subtle vertical gradient
        for y in range(height):
            # Gradually darken from top to bottom (very subtle)
            ratio = y / height
            darkening_factor = 0.95 + (ratio * 0.05)  # 95% to 100% of original brightness

            adjusted_color = (
                int(color[0] * darkening_factor),
                int(color[1] * darkening_factor),
                int(color[2] * darkening_factor)
            )

            pygame.draw.line(surface, adjusted_color, (0, y), (width, y))

        return surface

    def load_background_image(self, image_url: str, width: int, height: int) -> Optional[pygame.Surface]:
        """Load and cache a background image from URL or local path."""
        cache_key = f"{image_url}_{width}_{height}"

        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        try:
            # Check if it's a URL or local path
            if image_url.startswith(('http://', 'https://')):
                # Download to temporary location
                cache_dir = os.path.expanduser('~/.cache/nownextboard')
                os.makedirs(cache_dir, exist_ok=True)

                filename = os.path.basename(image_url.split('?')[0])
                if not filename or filename == '':
                    filename = f"image_{hash(image_url)}.jpg"
                local_path = os.path.join(cache_dir, filename)

                if not os.path.exists(local_path):
                    urllib.request.urlretrieve(image_url, local_path)

                image_path = local_path
            else:
                image_path = image_url

            # Load and scale the image
            image = pygame.image.load(image_path)
            image = pygame.transform.scale(image, (width, height))

            # Create a surface with the image at reduced opacity
            surface = pygame.Surface((width, height))
            surface.fill((255, 255, 255))  # White background

            # Set alpha for the image (30% opacity)
            image.set_alpha(int(255 * 0.3))
            surface.blit(image, (0, 0))

            self.image_cache[cache_key] = surface
            return surface

        except Exception as e:
            print(f"Failed to load background image {image_url}: {e}")
            return None

    def draw_activity_card(self, x: int, y: int, width: int, height: int,
                          activity: Optional[Dict[str, Any]], label: str,
                          is_current: bool = False):
        """Draw an activity card."""
        # Create a surface for the card
        card_surface = pygame.Surface((width, height))
        card_surface.fill((255, 255, 255))

        # Draw background
        if activity:
            image_url = activity.get('background_image')

            if image_url and image_url.strip() != '':
                # Try to load provided image
                bg_image = self.load_background_image(image_url, width, height)
                if bg_image:
                    card_surface.blit(bg_image, (0, 0))
                else:
                    # Fallback to gradient if image fails
                    color = self.get_auto_background_color(activity['name'])
                    gradient = self.create_gradient_background(width, height, color)
                    # Apply reduced opacity
                    gradient.set_alpha(int(255 * 0.3))
                    card_surface.blit(gradient, (0, 0))
            else:
                # No image provided - use calming gradient background
                color = self.get_auto_background_color(activity['name'])
                gradient = self.create_gradient_background(width, height, color)
                # Apply reduced opacity
                gradient.set_alpha(int(255 * 0.3))
                card_surface.blit(gradient, (0, 0))

        # Draw the card surface with rounded corners
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, (255, 255, 255, 255), (0, 0, width, height),
                        border_radius=15)

        # Blit card content onto temp surface
        temp_surface.blit(card_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Draw to screen
        self.screen.blit(temp_surface, (x, y))

        # Draw border for current activity
        if is_current:
            pygame.draw.rect(self.screen, BORDER_COLOR, (x, y, width, height),
                           3, border_radius=15)

        if not activity:
            # No activity - show placeholder
            text_surf = self.font_medium.render("No activity", True, TEXT_LIGHT_COLOR)
            text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(text_surf, text_rect)
            return

        # Draw label (NOW/NEXT) at top
        label_surf = self.font_label.render(label, True, TEXT_LIGHT_COLOR)
        label_rect = label_surf.get_rect(centerx=x + width // 2)
        label_rect.top = y + CARD_PADDING
        self.screen.blit(label_surf, label_rect)

        # Draw time (large and prominent, centered)
        time_text = f"{activity['start_time']}"
        time_surf = self.font_large.render(time_text, True, TEXT_COLOR)
        time_rect = time_surf.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(time_surf, time_rect)

        # Draw activity name (smaller, wrapped, at bottom)
        max_text_width = width - (CARD_PADDING * 2)
        name_lines = self.wrap_text(activity['name'], self.font_small, max_text_width)

        # Start from bottom and work up
        current_y = y + height - CARD_PADDING
        for line in reversed(name_lines):
            line_surf = self.font_small.render(line, True, TEXT_LIGHT_COLOR)
            line_rect = line_surf.get_rect(centerx=x + width // 2)
            line_rect.bottom = current_y
            self.screen.blit(line_surf, line_rect)
            current_y = line_rect.top - 5

    def draw_time_remaining(self, x: int, y: int, width: int,
                           remaining_seconds: int):
        """Draw time remaining text."""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        if minutes > 0:
            time_text = f"{minutes}m {seconds}s remaining"
        else:
            time_text = f"{seconds}s remaining"

        text_surf = self.font_small.render(time_text, True, TEXT_LIGHT_COLOR)
        text_rect = text_surf.get_rect(centerx=x + width // 2, centery=y)
        self.screen.blit(text_surf, text_rect)

    def render(self, current_activity: Optional[Dict[str, Any]],
              next_activity: Optional[Dict[str, Any]],
              time_info: Optional[Dict[str, Any]]):
        """Render the complete display."""
        # Clear screen
        self.screen.fill(BG_COLOR)

        # Draw timer border around screen edge if we have time info
        if time_info and current_activity:
            progress = time_info['progress_percent']
            self.draw_border_timer(progress)

        # Calculate layout with space for the outer ring
        # Add extra padding to keep cards inside the ring
        inner_padding = PADDING + RING_THICKNESS + 10
        card_width = (self.width - inner_padding * 3) // 2
        card_height = self.height - inner_padding * 2

        # Draw NOW card (left side)
        self.draw_activity_card(
            inner_padding, inner_padding, card_width, card_height,
            current_activity, "NOW", is_current=True
        )

        # Draw NEXT card (right side)
        self.draw_activity_card(
            inner_padding * 2 + card_width, inner_padding, card_width, card_height,
            next_activity, "NEXT", is_current=False
        )

        # Draw time remaining at bottom center if we have time info
        if time_info and current_activity:
            time_y = self.height - inner_padding // 2
            self.draw_time_remaining(0, time_y, self.width,
                                    time_info['remaining_seconds'])

        # Update display
        pygame.display.flip()

    def render_error(self, message: str):
        """Render an error message."""
        self.screen.fill(BG_COLOR)

        error_surf = self.font_medium.render("Error", True, (200, 50, 50))
        error_rect = error_surf.get_rect(center=(self.width // 2, self.height // 2 - 40))
        self.screen.blit(error_surf, error_rect)

        msg_surf = self.font_small.render(message, True, TEXT_LIGHT_COLOR)
        msg_rect = msg_surf.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(msg_surf, msg_rect)

        pygame.display.flip()

    def render_loading(self):
        """Render a loading screen."""
        self.screen.fill(BG_COLOR)

        text_surf = self.font_medium.render("Loading...", True, TEXT_LIGHT_COLOR)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surf, text_rect)

        pygame.display.flip()
