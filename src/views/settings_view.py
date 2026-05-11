import arcade

from data.settings import SETTINGS

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

class SettingsView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

        self.waiting_for_key = None
        self.control_options = {
            "Arriba": "key_up",
            "Abajo": "key_down",
            "Izquierda": "key_left",
            "Derecha": "key_right",
            "Dash": "key_dash",
            "Pausa": "key_pause",
            "Reiniciar": "key_restart",
        }

    def on_draw(self):
        # Dibujamos el juego congelado detrás
        self.game_view.on_draw()

        # Capa oscura encima del juego
        arcade.draw_rect_filled(
            arcade.LBWH(
                0,
                0,
                WINDOW_WIDTH,
                WINDOW_HEIGHT
            ),
            (80, 80, 80, 170),
        )

        arcade.draw_text(
            "AJUSTES",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - 120,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )

        arcade.draw_text(
            "Aquí irán los ajustes del juego",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 30,
            arcade.color.WHITE,
            22,
            anchor_x="center",
        )

        arcade.draw_rect_filled(
            arcade.LRBT(
                WINDOW_WIDTH / 2 - 130,
                WINDOW_WIDTH / 2 + 130,
                120 - 26,
                120 + 26,
            ),
            (180, 140, 40, 180),
        )   

        arcade.draw_text(
            "Volver",
            WINDOW_WIDTH / 2,
            120,
            arcade.color.GOLD,
            26,
            anchor_x="center",
            anchor_y="center",
        )

        arcade.draw_text(
            "Esc / Enter / Click",
            WINDOW_WIDTH / 2,
            65,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        from views.pause_view import PauseMenuView
        if key in (arcade.key.ESCAPE, arcade.key.ENTER, arcade.key.SPACE, arcade.key.BACKSPACE):
            self.window.show_view(PauseMenuView(self.game_view))

    def on_mouse_press(self, x, y, button, modifiers):
        from views.pause_view import PauseMenuView
        if 120 - 26 <= y <= 120 + 26 and (WINDOW_WIDTH / 2 - 130) <= x <= (WINDOW_WIDTH / 2 + 130):
            self.window.show_view(PauseMenuView(self.game_view))
    
    def toggle_fullscreen(self):
        SETTINGS.fullscreen = not SETTINGS.fullscreen

        self.window.set_fullscreen(SETTINGS.fullscreen)

        # Reajustar viewport
        self.window.set_viewport(
            0,
            self.window.width,
            0,
            self.window.height
        )