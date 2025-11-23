"""Rendering logic for the Now-Next board display."""
import pygame
import math
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

    def draw_timer_ring(self, center_x: int, center_y: int, radius: int,
                       progress_percent: float):
        """Draw a circular timer ring showing progress."""
        # Draw elapsed (background) ring
        pygame.draw.circle(self.screen, RING_ELAPSED_COLOR,
                          (center_x, center_y), radius, RING_THICKNESS)

        # Draw remaining (foreground) ring
        if progress_percent > 0:
            # Calculate arc angle (pygame uses radians, 0 is at 3 o'clock)
            # We want to start at 12 o'clock and go clockwise
            start_angle = -math.pi / 2  # 12 o'clock
            end_angle = start_angle + (2 * math.pi * (progress_percent / 100))

            # Draw arc segments to create smooth ring
            num_segments = max(int(progress_percent * 3.6), 1)  # More segments for smoother arc
            angle_step = (end_angle - start_angle) / num_segments

            for i in range(num_segments):
                angle1 = start_angle + (i * angle_step)
                angle2 = start_angle + ((i + 1) * angle_step)

                # Calculate points for this segment
                x1_outer = center_x + int((radius) * math.cos(angle1))
                y1_outer = center_y + int((radius) * math.sin(angle1))
                x2_outer = center_x + int((radius) * math.cos(angle2))
                y2_outer = center_y + int((radius) * math.sin(angle2))

                x1_inner = center_x + int((radius - RING_THICKNESS) * math.cos(angle1))
                y1_inner = center_y + int((radius - RING_THICKNESS) * math.sin(angle1))
                x2_inner = center_x + int((radius - RING_THICKNESS) * math.cos(angle2))
                y2_inner = center_y + int((radius - RING_THICKNESS) * math.sin(angle2))

                # Draw the segment as a polygon
                points = [(x1_outer, y1_outer), (x2_outer, y2_outer),
                         (x2_inner, y2_inner), (x1_inner, y1_inner)]
                pygame.draw.polygon(self.screen, RING_REMAINING_COLOR, points)

    def draw_activity_card(self, x: int, y: int, width: int, height: int,
                          activity: Optional[Dict[str, Any]], label: str,
                          is_current: bool = False):
        """Draw an activity card."""
        # Draw card background
        card_color = (255, 255, 255)
        pygame.draw.rect(self.screen, card_color, (x, y, width, height),
                        border_radius=15)

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

        # Draw label (NOW/NEXT)
        label_surf = self.font_label.render(label, True, TEXT_LIGHT_COLOR)
        self.screen.blit(label_surf, (x + CARD_PADDING, y + CARD_PADDING))

        # Draw icon/emoji if present
        icon_y = y + CARD_PADDING + 40
        if activity.get('icon'):
            icon_surf = self.font_large.render(activity['icon'], True, TEXT_COLOR)
            icon_rect = icon_surf.get_rect(centerx=x + width // 2)
            icon_rect.top = icon_y
            self.screen.blit(icon_surf, icon_rect)
            icon_y = icon_rect.bottom + 20

        # Draw activity name
        name_surf = self.font_medium.render(activity['name'], True, TEXT_COLOR)
        name_rect = name_surf.get_rect(centerx=x + width // 2)
        name_rect.top = icon_y
        self.screen.blit(name_surf, name_rect)

        # Draw time
        time_y = name_rect.bottom + 15
        time_text = f"{activity['start_time']}"
        time_surf = self.font_small.render(time_text, True, TEXT_LIGHT_COLOR)
        time_rect = time_surf.get_rect(centerx=x + width // 2)
        time_rect.top = time_y
        self.screen.blit(time_surf, time_rect)

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

        # Calculate layout
        card_width = (self.width - PADDING * 3) // 2
        card_height = self.height - PADDING * 2

        # Draw NOW card (left side)
        self.draw_activity_card(
            PADDING, PADDING, card_width, card_height,
            current_activity, "NOW", is_current=True
        )

        # Draw NEXT card (right side)
        self.draw_activity_card(
            PADDING * 2 + card_width, PADDING, card_width, card_height,
            next_activity, "NEXT", is_current=False
        )

        # Draw timer ring around NOW card if we have time info
        if time_info and current_activity:
            ring_center_x = PADDING + card_width // 2
            ring_center_y = PADDING + card_height // 2
            ring_radius = min(card_width, card_height) // 2 - 40

            progress = time_info['progress_percent']
            self.draw_timer_ring(ring_center_x, ring_center_y, ring_radius, progress)

            # Draw time remaining at bottom of NOW card
            time_y = PADDING + card_height - 60
            self.draw_time_remaining(PADDING, time_y, card_width,
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
