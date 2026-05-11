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

def main():
    """Main function"""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
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
    main()