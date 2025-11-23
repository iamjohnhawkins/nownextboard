"""Main application for Now-Next Board display."""
import pygame
import requests
import time
import sys
import os
from typing import Optional, Dict, Any, Tuple

from config import *
from renderer import Renderer


class NowNextBoard:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        # For framebuffer mode (no X server), set SDL to use framebuffer
        # This must be done before pygame.init()
        if USE_FRAMEBUFFER:
            print("Framebuffer mode enabled (experimental)")
            print("Note: HyperPixel 4 typically requires X server")
            print("If you get errors, set USE_FRAMEBUFFER=False in config.py")
            os.environ['SDL_VIDEODRIVER'] = 'fbcon'
            os.environ['SDL_FBDEV'] = '/dev/fb0'
            os.environ['SDL_NOMOUSE'] = '1'

        pygame.init()

        # Set up display
        if FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("Now-Next Board")

        # Hide mouse cursor in fullscreen
        if FULLSCREEN:
            pygame.mouse.set_visible(False)

        # Initialize renderer
        self.renderer = Renderer(self.screen)

        # Application state
        self.running = True
        self.last_poll = 0
        self.current_data = None
        self.clock = pygame.time.Clock()

    def fetch_current_activities(self) -> Optional[Dict[str, Any]]:
        """Fetch current and next activities from API."""
        try:
            response = requests.get(f"{API_URL}/api/current", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Failed to fetch activities: {e}")
            return None

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Refresh data immediately
                    self.last_poll = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle touch events if needed
                pass

    def update(self):
        """Update application state."""
        current_time = time.time()

        # Poll API at regular intervals
        if current_time - self.last_poll >= POLL_INTERVAL:
            data = self.fetch_current_activities()
            if data:
                self.current_data = data
            self.last_poll = current_time

    def render(self):
        """Render the current state."""
        if self.current_data is None:
            self.renderer.render_loading()
        else:
            current = self.current_data.get('current')
            next_act = self.current_data.get('next')
            time_info = self.current_data.get('time_info')

            self.renderer.render(current, next_act, time_info)

    def run(self):
        """Main application loop."""
        print("Now-Next Board starting...")
        print(f"Connecting to API at {API_URL}")

        # Initial data fetch
        self.renderer.render_loading()
        self.current_data = self.fetch_current_activities()

        if self.current_data is None:
            print("Warning: Could not connect to API. Will keep trying...")

        # Main loop
        while self.running:
            self.handle_events()
            self.update()
            self.render()

            # Limit to 30 FPS
            self.clock.tick(30)

        print("Shutting down...")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = NowNextBoard()
    app.run()
