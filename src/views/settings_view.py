import arcade

from constants import *

from data.settings import SETTINGS
from pyglet.window import key as pyglet_key

class SettingsView(arcade.View):

    def __init__(self, previous_view):

        super().__init__()

        self.previous_view = previous_view

        self.selected_index = 0

        self.waiting_for_key = None

        self.options = [

            # AUDIO
            ("Music Volume", "music"),
            ("Voice Volume", "voice"),
            ("SFX Volume", "sfx"),

            # VIDEO
            ("Fullscreen", "fullscreen"),

            # CONTROLS
            ("Arriba", "key_up"),
            ("Abajo", "key_down"),
            ("Izquierda", "key_left"),
            ("Derecha", "key_right"),
            ("Dash", "key_dash"),
            ("Pausa", "key_pause"),
            ("Reiniciar", "key_restart"),

            # BACK
            ("Volver", "back"),
        ]

        self.conflicting_actions = set()

    def on_draw(self):
        screen_width = self.window.width
        screen_height = self.window.height

        self.previous_view.on_draw()

        arcade.draw_rect_filled(
            arcade.LBWH(
                0,
                0,
                screen_width,
                screen_height
            ),
            (40, 40, 40, 220),
        )

        arcade.draw_text(
            "AJUSTES",
            screen_width / 2,
            screen_height - 80,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )

        start_y = screen_height - 170
        gap = 45

        for i, (label, action) in enumerate(self.options):

            y = start_y - i * gap

            selected = i == self.selected_index

            if action in self.conflicting_actions:
                color = arcade.color.RED

            elif selected:
                color = arcade.color.GOLD

            else:
                color = arcade.color.WHITE

            value_text = self.get_value_text(action)

            arcade.draw_text(
                label,
                screen_width * 0.35,
                y,
                color,
                22,
                anchor_x="left"
            )

            arcade.draw_text(
                value_text,
                screen_width * 0.65,
                y,
                color,
                22,
                anchor_x="right"
            )

        if self.waiting_for_key:

            arcade.draw_text(
                "Press any key...",
                screen_width / 2,
                90,
                arcade.color.RED,
                24,
                anchor_x="center"
            )
    
        if len(self.conflicting_actions) > 0:
            arcade.draw_text(
                "Cada control debe tener una tecla única",
                screen_width / 2,
                40,
                arcade.color.RED,
                20,
                anchor_x="center"
            )

    def get_value_text(self, action):

        if action == "music":
            return f"{int(SETTINGS.music_volume * 100)}%"

        if action == "voice":
            return f"{int(SETTINGS.voice_volume * 100)}%"

        if action == "sfx":
            return f"{int(SETTINGS.sfx_volume * 100)}%"

        if action == "fullscreen":
            return "ON" if SETTINGS.fullscreen else "OFF"

        if hasattr(SETTINGS, action):

            key = getattr(SETTINGS, action)

            return pyglet_key.symbol_string(key)

        return ""
    
    def validate_unique_keys(self):

        self.conflicting_actions.clear()

        key_map = {}

        for _, action in self.options:

            if action.startswith("key_"):

                key_value = getattr(SETTINGS, action)

                if key_value in key_map:

                    self.conflicting_actions.add(action)
                    self.conflicting_actions.add(key_map[key_value])

                else:
                    key_map[key_value] = action

        return len(self.conflicting_actions) == 0

    def on_key_press(self, key, modifiers):

        # REBINDING
        if self.waiting_for_key:
            setattr(
                SETTINGS,
                self.waiting_for_key,
                key
            )

            SETTINGS.save()

            self.validate_unique_keys()

            self.waiting_for_key = None

            return

        # NAVIGATION
        if key in (arcade.key.UP, arcade.key.W):

            self.selected_index -= 1

            if self.selected_index < 0:
                self.selected_index = len(self.options) - 1

        elif key in (arcade.key.DOWN, arcade.key.S):

            self.selected_index += 1

            if self.selected_index >= len(self.options):
                self.selected_index = 0

        elif key in (arcade.key.LEFT, arcade.key.A):

            self.change_current_value(-0.1)

        elif key in (arcade.key.RIGHT, arcade.key.D):

            self.change_current_value(0.1)

        elif key in (
            arcade.key.ENTER,
            arcade.key.SPACE
        ):

            self.activate_option()

        elif key == arcade.key.ESCAPE:

            self.go_back()

    def change_current_value(self, amount):

        _, action = self.options[self.selected_index]

        if action == "music":

            SETTINGS.music_volume = max(
                0,
                min(1, SETTINGS.music_volume + amount)
            )

        elif action == "voice":

            SETTINGS.voice_volume = max(
                0,
                min(1, SETTINGS.voice_volume + amount)
            )

        elif action == "sfx":

            SETTINGS.sfx_volume = max(
                0,
                min(1, SETTINGS.sfx_volume + amount)
            )

        SETTINGS.save()

        # Actualizar volumen realtime
        if action == "music":

            if hasattr(
                self.previous_view,
                "update_music_volume"
            ):

                self.previous_view.update_music_volume()

        SETTINGS.save()

    def activate_option(self):

        _, action = self.options[self.selected_index]

        if action == "fullscreen":

            from views.game_view import GameView
            from views.menu_view import MainMenu
            from views.pause_view import PauseMenuView

            # Guardar nuevo estado
            SETTINGS.fullscreen = not SETTINGS.fullscreen
            SETTINGS.save()

            # Limpiar vistas antiguas
            if hasattr(self.previous_view, "cleanup"):
                self.previous_view.cleanup()

            # Cambiar fullscreen
            self.window.set_fullscreen(SETTINGS.fullscreen)

            # FORZAR resize real
            self.window.dispatch_event(
                "on_resize",
                self.window.width,
                self.window.height
            )

            # ======================
            # VENIMOS DEL PAUSE
            # ======================
            if isinstance(self.previous_view, PauseMenuView):

                old_game = self.previous_view.game_view

                new_game = GameView(level=old_game.level)

                new_game.setup()

                self.window.show_view(new_game)

            # ======================
            # VENIMOS DEL MENU
            # ======================
            elif isinstance(self.previous_view, MainMenu):

                new_menu = MainMenu()

                self.window.show_view(new_menu)

            return

        elif action.startswith("key_"):
            self.waiting_for_key = action

        elif action == "back":

            self.go_back()

    def go_back(self):

        if len(self.conflicting_actions) > 0:
            return

        self.window.show_view(
            self.previous_view
        )
        
    def stop_menu_media(self):
        if self.video:
            self.video.release()

        if self.music_player:
            self.music_player.pause()