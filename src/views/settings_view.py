import arcade

from data.settings import SETTINGS
from pyglet.window import key as pyglet_key


class SettingsView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()

        self.previous_view = previous_view
        self.selected_index = 0
        self.waiting_for_key = None
        self.conflicting_actions = set()
        self.option_hitboxes = []
        self.font_name = "Garamond"

        self.cream = (238, 230, 206)
        self.muted = (176, 166, 142)
        self.gold = (212, 165, 78)
        self.warning = (206, 82, 65)
        self.blue = (142, 190, 214)

        self.options = [
            ("Musica", "music", "audio"),
            ("Voces", "voice", "audio"),
            ("Efectos", "sfx", "audio"),
            ("Pantalla completa", "fullscreen", "video"),
            ("Arriba", "key_up", "controls"),
            ("Abajo", "key_down", "controls"),
            ("Izquierda", "key_left", "controls"),
            ("Derecha", "key_right", "controls"),
            ("Dash", "key_dash", "controls"),
            ("Disparar", "key_shoot", "controls"),
            ("Pausa", "key_pause", "controls"),
            ("Reiniciar", "key_restart", "controls"),
            ("Volver", "back", "back"),
        ]

        self.validate_unique_keys()

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

    def on_draw(self):
        width = self.window.width
        height = self.window.height
        self.option_hitboxes = []

        self.previous_view.on_draw()
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (4, 6, 11, 178))

        title_y = height - 92
        arcade.draw_text(
            "AJUSTES",
            width / 2,
            title_y,
            self.cream,
            40,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
            bold=False,
        )
        arcade.draw_line(width / 2 - 92, title_y - 34, width / 2 + 92, title_y - 34, (212, 165, 78, 92), 1)

        left_x = width * 0.25
        right_x = width * 0.62
        audio_y = height - 170
        controls_y = height - 170
        gap = 40 if height >= 650 else 34

        self._draw_section("AUDIO", left_x, audio_y)
        self._draw_option(0, left_x, audio_y - gap, width * 0.28)
        self._draw_option(1, left_x, audio_y - gap * 2, width * 0.28)
        self._draw_option(2, left_x, audio_y - gap * 3, width * 0.28)

        video_y = audio_y - gap * 4.5
        self._draw_section("VIDEO", left_x, video_y)
        self._draw_option(3, left_x, video_y - gap, width * 0.28)

        self._draw_section("CONTROLES", right_x, controls_y)
        control_indices = [
            i for i, (_label, _action, section) in enumerate(self.options)
            if section == "controls"
        ]
        for row, option_index in enumerate(control_indices):
            self._draw_option(option_index, right_x, controls_y - gap * (row + 1), width * 0.24)

        back_index = next(
            i for i, (_label, _action, section) in enumerate(self.options)
            if section == "back"
        )
        self._draw_option(back_index, width / 2 - 110, 78, 220)

        if self.waiting_for_key:
            self._draw_waiting_message(width, height)
        elif self.conflicting_actions:
            self._draw_warning(width)

    def _draw_section(self, title, x, y):
        arcade.draw_text(
            title,
            x,
            y,
            self.muted,
            14,
            anchor_x="left",
            anchor_y="center",
            font_name=self.font_name,
            bold=True,
        )

    def _draw_option(self, index, x, y, width):
        label, action, _section = self.options[index]
        selected = index == self.selected_index
        conflict = action in self.conflicting_actions

        row_height = 30
        left = x - 10
        right = x + width
        bottom = y - row_height / 2
        top = y + row_height / 2
        self.option_hitboxes.append((index, left, right, bottom, top))

        color = self.warning if conflict else self.cream
        value_color = self.warning if conflict else self.muted
        if selected:
            color = self.gold if not conflict else self.warning
            value_color = self.cream if not conflict else self.warning
            arcade.draw_rect_filled(
                arcade.LBWH(left, bottom, width + 20, row_height),
                (255, 255, 255, 13),
            )
            arcade.draw_line(left, bottom, left, top, (212, 165, 78, 145), 2)

        arcade.draw_text(
            label,
            x,
            y,
            color,
            20 if selected else 18,
            anchor_x="left",
            anchor_y="center",
            font_name=self.font_name,
            bold=False,
        )

        if action in ("music", "voice", "sfx"):
            value = self._volume_value(action)
            self._draw_slider(x + width * 0.48, y, width * 0.36, value, selected)
            arcade.draw_text(
                f"{int(value * 100)}%",
                x + width,
                y,
                value_color,
                16,
                anchor_x="right",
                anchor_y="center",
                font_name=self.font_name,
            )
            return

        value_text = self.get_value_text(action)
        if action == "fullscreen" and SETTINGS.fullscreen:
            value_color = self.blue
        if action == "back":
            value_color = self.gold if selected else self.muted

        arcade.draw_text(
            value_text,
            x + width,
            y,
            value_color,
            17,
            anchor_x="right",
            anchor_y="center",
            font_name=self.font_name,
        )

    def _draw_slider(self, x, y, width, value, selected):
        arcade.draw_line(x, y, x + width, y, (160, 150, 130, 72), 3)
        arcade.draw_line(
            x,
            y,
            x + width * value,
            y,
            self.gold if selected else (142, 190, 214, 150),
            3,
        )
        arcade.draw_circle_filled(
            x + width * value,
            y,
            5 if selected else 4,
            self.cream if selected else self.muted,
        )

    def _draw_waiting_message(self, width, height):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (0, 0, 0, 120))
        arcade.draw_text(
            "Pulsa una tecla",
            width / 2,
            height / 2 + 14,
            self.cream,
            30,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )
        arcade.draw_text(
            "Se guardara al instante",
            width / 2,
            height / 2 - 22,
            self.muted,
            17,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )

    def _draw_warning(self, width):
        arcade.draw_text(
            "Cada control debe tener una tecla unica",
            width / 2,
            38,
            self.warning,
            18,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )

    def _volume_value(self, action):
        if action == "music":
            return SETTINGS.music_volume
        if action == "voice":
            return SETTINGS.voice_volume
        return SETTINGS.sfx_volume

    def get_value_text(self, action):
        if action == "music":
            return f"{int(SETTINGS.music_volume * 100)}%"
        if action == "voice":
            return f"{int(SETTINGS.voice_volume * 100)}%"
        if action == "sfx":
            return f"{int(SETTINGS.sfx_volume * 100)}%"
        if action == "fullscreen":
            return "< ON >" if SETTINGS.fullscreen else "< OFF >"
        if action == "back":
            return "Salir"
        if hasattr(SETTINGS, action):
            key = getattr(SETTINGS, action)
            return pyglet_key.symbol_string(key)
        return ""

    def validate_unique_keys(self):
        self.conflicting_actions.clear()
        key_map = {}

        for _label, action, _section in self.options:
            if action.startswith("key_"):
                key_value = getattr(SETTINGS, action)
                if key_value in key_map:
                    self.conflicting_actions.add(action)
                    self.conflicting_actions.add(key_map[key_value])
                else:
                    key_map[key_value] = action

        return len(self.conflicting_actions) == 0

    def on_key_press(self, key, modifiers):
        if self.waiting_for_key:
            setattr(SETTINGS, self.waiting_for_key, key)
            SETTINGS.save()
            self.validate_unique_keys()
            self.waiting_for_key = None
            return

        if key in (arcade.key.UP, arcade.key.W):
            self.selected_index = (self.selected_index - 1) % len(self.options)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.change_current_value(-0.1)
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.change_current_value(0.1)
        elif key in (arcade.key.ENTER, arcade.key.SPACE):
            self.activate_option()
        elif key == arcade.key.ESCAPE:
            self.go_back()

    def on_mouse_motion(self, x, y, dx, dy):
        for index, left, right, bottom, top in self.option_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = index
                return

    def on_mouse_press(self, x, y, button, modifiers):
        for index, left, right, bottom, top in self.option_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = index
                _label, action, _section = self.options[index]

                if action in ("music", "voice", "sfx"):
                    slider_left = left + (right - left) * 0.48
                    slider_width = (right - left) * 0.36
                    value = (x - slider_left) / slider_width
                    self.set_volume(action, value)
                else:
                    self.activate_option()
                return

    def change_current_value(self, amount):
        _label, action, _section = self.options[self.selected_index]

        if action == "music":
            self.set_volume("music", SETTINGS.music_volume + amount)
        elif action == "voice":
            self.set_volume("voice", SETTINGS.voice_volume + amount)
        elif action == "sfx":
            self.set_volume("sfx", SETTINGS.sfx_volume + amount)

    def set_volume(self, action, value):
        value = max(0, min(1, value))

        if action == "music":
            SETTINGS.music_volume = value
        elif action == "voice":
            SETTINGS.voice_volume = value
        elif action == "sfx":
            SETTINGS.sfx_volume = value

        SETTINGS.save()

        if action == "music" and hasattr(self.previous_view, "update_music_volume"):
            self.previous_view.update_music_volume()

    def activate_option(self):
        _label, action, _section = self.options[self.selected_index]

        if action == "fullscreen":
            self.toggle_fullscreen()
        elif action.startswith("key_"):
            self.waiting_for_key = action
        elif action == "back":
            self.go_back()

    def toggle_fullscreen(self):
        from views.game_view import GameView
        from views.menu_view import MainMenu
        from views.pause_view import PauseMenuView

        SETTINGS.fullscreen = not SETTINGS.fullscreen
        SETTINGS.save()

        if hasattr(self.previous_view, "cleanup"):
            self.previous_view.cleanup()

        self.window.set_fullscreen(SETTINGS.fullscreen)
        self.window.dispatch_event(
            "on_resize",
            self.window.width,
            self.window.height,
        )

        if isinstance(self.previous_view, PauseMenuView):
            old_game = self.previous_view.game_view
            new_game = GameView(
                level=old_game.level,
                score=old_game.score,
                lives=old_game.lives,
                room_position=old_game.current_room,
                entry_side=old_game.entry_side,
            )
            self.window.show_view(new_game)
        elif isinstance(self.previous_view, MainMenu):
            self.window.show_view(MainMenu())

    def go_back(self):
        if self.conflicting_actions:
            return

        self.window.show_view(self.previous_view)
