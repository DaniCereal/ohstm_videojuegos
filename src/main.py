"""
Platformer Game. 

Basado en el tutorial de arcade: https://arcade.academy/examples/platform_tutorial.html#platform-tutorial
"""
import math

from pathlib import Path

import arcade

from data.settings import SETTINGS
from views.menu_view import MainMenu
from constants import *

import os
os.chdir(Path(__file__).parent)

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
    window.ctx.viewport = (0, 0, window.width, window.height)
    menu_view = MainMenu()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":

    # Obtenemos la ruta del proyecto utilizando PathLib,
    # necesitamos esta ruta para poder acceder a los archivos con recursos
    # de forma independiente desde donde se ejecute el script.
    PROJECT_ROOT = Path(__file__).parent.parent

    print(f"Project root is: {PROJECT_ROOT}")

    # Ejemplo de acceso a un archivo dentro de recursos
    #filetest = PROJECT_ROOT / "assets" / "dialogs.txt"
    #print(f"Test file size: {filetest.stat().st_size} bytes")
    
    SETTINGS.load()
    SETTINGS.fullscreen = False
    SETTINGS.save()

    main()