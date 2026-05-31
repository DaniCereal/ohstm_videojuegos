"""
Platformer Game.

Basado en el tutorial de arcade: https://arcade.academy/examples/platform_tutorial.html#platform-tutorial
"""
from pathlib import Path

import arcade

from data.settings import SETTINGS
from views.menu_view import MainMenu
from constants import *

def main():
    """Main function"""
    window = arcade.Window(
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        title=WINDOW_TITLE,
        resizable=True,
        update_rate=1/60
    )

    window.set_minimum_size(640, 360)
    window.center_window()
    if SETTINGS.fullscreen:
        window.set_fullscreen(True)
    window.ctx.viewport = (0, 0, window.width, window.height)
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).parent.parent
    print(f"Project root is: {PROJECT_ROOT}")

    SETTINGS.load()

    main()
