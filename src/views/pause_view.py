import arcade

from views.settings_view import SettingsView

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

class PauseMenuView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.selected_index = 0

        self.options = [
            ("Reanudar", self.resume_game),
            ("Ajustes", self.open_settings),
            ("Reiniciar nivel", self.restart_level),
            ("Menú principal", self.go_main_menu),
        ]

        # CAMBIAR PNG POR NUESTRO PERSONAJE
        self.character_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        )

    def on_draw(self):
        # Dibujamos el juego congelado debajo
        self.game_view.on_draw()

        # Filtro grisáceo
        arcade.draw_rect_filled(
            arcade.LBWH(
                0,
                0,
                WINDOW_WIDTH,
                WINDOW_HEIGHT
            ),
            (80, 80, 80, 170),
        )

        # Imagen grande del personaje a la izquierda
        arcade.draw_texture_rect(
            self.character_texture,
            arcade.LBWH(
                100,
                WINDOW_HEIGHT / 2 - 200,
                self.character_texture.width * 5,
                self.character_texture.height * 5,
            ),
        )

        # Título
        arcade.draw_text(
            "PAUSA",
            WINDOW_WIDTH * 0.74,
            WINDOW_HEIGHT - 120,
            arcade.color.WHITE,
            42,
            anchor_x="center",
        )

        # Opciones
        start_y = WINDOW_HEIGHT * 0.60
        gap = 72
        x = WINDOW_WIDTH * 0.74

        for i, (label, _) in enumerate(self.options):
            y = start_y - i * gap
            is_selected = i == self.selected_index

            if is_selected:
                arcade.draw_rect_filled(
                    arcade.LRBT(
                        x - 190,
                        x + 190,
                        y - 24,
                        y + 24,
                    ),
                    (180, 140, 40, 180),
                )

            arcade.draw_text(
                label,
                x,
                y,
                arcade.color.GOLD if is_selected else arcade.color.WHITE,
                26,
                anchor_x="center",
                anchor_y="center",
            )

        arcade.draw_text(
            "↑ ↓ / W S  ·  Enter  ·  Esc",
            WINDOW_WIDTH * 0.74,
            70,
            arcade.color.WHITE,
            16,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.BACKSPACE):
            self.resume_game()
            return

        if key in (arcade.key.UP, arcade.key.W):
            self.selected_index = (self.selected_index - 1) % len(self.options)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif key in (arcade.key.ENTER, arcade.key.SPACE):
            self.activate_selected()

    def on_mouse_motion(self, x, y, dx, dy):
        self.selected_index = self._get_option_index_at(x, y, self.selected_index)

    def on_mouse_press(self, x, y, button, modifiers):
        self.selected_index = self._get_option_index_at(x, y, self.selected_index)
        self.activate_selected()

    def _get_option_index_at(self, x, y, default_index):
        start_y = WINDOW_HEIGHT * 0.60
        gap = 72
        center_x = WINDOW_WIDTH * 0.74
        box_w = 380
        box_h = 48

        for i in range(len(self.options)):
            option_y = start_y - i * gap
            left = center_x - box_w / 2
            right = center_x + box_w / 2
            bottom = option_y - box_h / 2
            top = option_y + box_h / 2

            if left <= x <= right and bottom <= y <= top:
                return i

        return default_index

    def activate_selected(self):
        _, action = self.options[self.selected_index]
        action()

    def resume_game(self):
        self.window.show_view(self.game_view)

    def open_settings(self):
        self.window.show_view(SettingsView(self.game_view))

    def restart_level(self):
        self.game_view.setup()
        self.window.show_view(self.game_view)

    def go_main_menu(self):
        from views.menu_view import MainMenu
        self.window.show_view(MainMenu())