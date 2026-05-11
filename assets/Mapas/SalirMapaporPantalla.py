import arcade

# Configuración de la ventana
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Cargando mapa de Tiled con Arcade"

class MiJuego(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Aquí guardaremos nuestra escena (que contendrá el mapa)
        self.scene = None

    def setup(self):
        """ Configura el juego y carga el mapa. """
        
        # 1. Ruta a tu archivo .tmx (NO al .world)
        ruta_mapa = "Infierno1.2.tmx"  # Asegúrate de que este archivo esté en el mismo directorio o proporciona la ruta correcta

        # 2. Cargar el mapa (scaling permite hacer los gráficos más grandes o pequeños)
        opciones_capas = {
            # Si tienes capas específicas en Tiled, puedes darles propiedades aquí
            # "Paredes": {"use_spatial_hash": True},
        }
        
        mapa_tiled = arcade.tilemap.load_tilemap(ruta_mapa, scaling=1.0, layer_options=opciones_capas)

        # 3. Crear una Escena de Arcade a partir del mapa
        self.scene = arcade.Scene.from_tilemap(mapa_tiled)

        # Establecer un color de fondo
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

    def on_draw(self):
        """ Renderiza los elementos en pantalla. """
        self.clear()
        
        # Esto dibuja automáticamente todas las capas del mapa de Tiled
        self.scene.draw()

def main():
    window = MiJuego()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()