"""Main application for Now-Next Board display."""
import pygame
import requests
import time
import sys
import os
from typing import Optional, Dict, Any, Tuple

from config import *
from renderer import Renderer


def choose_backend():
    """
    Choose SDL video backend with priority:
      1) Respect user overrides (SDL_VIDEODRIVER already set)
      2) KMSDRM on card2, card1, card0
      3) fbdev on /dev/fb0
    Returns: (backend_env: dict, phys_w, phys_h)
    """
    def file_exists(p):
        try:
            return os.path.exists(p)
        except Exception:
            return False

    def try_init_display(env: dict, probe_size=(800, 480)):
        """Attempt to init pygame display with given env. Return (ok, info_or_error)."""
        # Apply env for this attempt
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = str(v)

        print(f"  Testing with env: {', '.join(f'{k}={v}' for k, v in sorted(env.items()))}")

        try:
            pygame.display.init()
            pygame.font.init()
            flags = pygame.FULLSCREEN if FULLSCREEN else 0
            screen = pygame.display.set_mode(probe_size, flags)
            info = pygame.display.Info()
            drv = pygame.display.get_driver()
            print(f"  ✓ Display init OK: driver={drv} phys={info.current_w}x{info.current_h}")
            return True, (info.current_w, info.current_h, drv,
                          env.get("SDL_KMSDRM_DEVICE_INDEX"), env.get("SDL_FBDEV"))
        except Exception as e:
            print(f"  ✗ Display init failed: {e}")
            try:
                pygame.display.quit()
            except Exception:
                pass
            return False, str(e)

    # If user pre-set a driver, try it
    if os.getenv("SDL_VIDEODRIVER"):
        print(f"SDL_VIDEODRIVER preset: {os.getenv('SDL_VIDEODRIVER')}")
        try:
            pygame.init()
        except Exception as e:
            print(f"pygame.init warning: {e}")
        ok, info = try_init_display({}, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if ok:
            phys_w, phys_h, drv, idx, fb = info
            print(f"Using preset driver={drv} idx={idx} fb={fb}")
            return dict(os.environ), phys_w, phys_h
        else:
            print(f"Preset SDL_VIDEODRIVER failed: {info}")

    # Try KMSDRM on likely card indices
    print("Trying KMSDRM backend...")
    for idx in ("2", "1", "0"):
        env = {
            "SDL_VIDEODRIVER": "kmsdrm",
            "SDL_KMSDRM_DEVICE_INDEX": idx,
            "PYGAME_HIDE_SUPPORT_PROMPT": "1",
            "XDG_RUNTIME_DIR": os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
            "SDL_NOMOUSE": "1",
        }
        ok, info = try_init_display(env, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if ok:
            phys_w, phys_h, drv, dev_idx, fb = info
            print(f"✓ Selected backend: driver={drv} kms_index={dev_idx} phys={phys_w}x{phys_h}")
            return env, phys_w, phys_h
        else:
            print(f"  KMSDRM idx {idx} failed, trying next...")

    # Fallback: fbdev on /dev/fb0
    print("Trying fbdev backend...")
    fbdev = "/dev/fb0" if file_exists("/dev/fb0") else None
    env = {
        "SDL_VIDEODRIVER": "fbdev",
        "SDL_FBDEV": fbdev,
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",
        "XDG_RUNTIME_DIR": os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"),
        "SDL_NOMOUSE": "1",
    }
    ok, info = try_init_display(env, (SCREEN_WIDTH, SCREEN_HEIGHT))
    if ok:
        phys_w, phys_h, drv, dev_idx, fb = info
        print(f"✓ Selected backend: driver={drv} fb={fb} phys={phys_w}x{phys_h}")
        return env, phys_w, phys_h

    raise SystemExit(f"[FATAL] Could not initialize any SDL video backend. Last error: {info}")


class NowNextBoard:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        print("=" * 60)
        print(">>> BOOT Now-Next Board Display")
        print("=" * 60)

        # Choose backend and get physical size
        backend_env, phys_w, phys_h = choose_backend()
        drv = backend_env.get("SDL_VIDEODRIVER")
        kms_idx = backend_env.get("SDL_KMSDRM_DEVICE_INDEX")
        fb = backend_env.get("SDL_FBDEV")

        print(f"Backend chosen: driver={drv} kms_index={kms_idx} fb={fb} phys={phys_w}x{phys_h}")
        print(f"Env summary: DISPLAY={os.getenv('DISPLAY')} XDG_RUNTIME_DIR={os.getenv('XDG_RUNTIME_DIR')}")

        # pygame already initialized by choose_backend()
        # Just init the modules we need
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
    # Warn if DISPLAY is set - we want to run natively without X server
    if os.getenv("DISPLAY"):
        print("WARNING: DISPLAY is set; recommended to run on console (no X/Wayland).")
        print("         Unset DISPLAY or run from TTY for best performance.")

    try:
        app = NowNextBoard()
        app.run()
    except SystemExit:
        raise
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        raise
