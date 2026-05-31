import arcade
from PIL import Image

from data.settings import SETTINGS
from views.settings_view import SettingsView

DUCK_FACTOR = 0.15


class PauseMenuView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.selected_index = 0
        self.font_name = "Garamond"

        self.cream = (238, 230, 206)
        self.muted = (176, 166, 142)
        self.gold = (212, 165, 78)

        self.options = [
            ("Reanudar", self.resume_game),
            ("Ajustes", self.open_settings),
            ("Menu principal", self.go_main_menu),
        ]

        self.fade_texture = self._create_fade_texture()
        self.button_hitboxes = []

        if game_view.music_player:
            game_view.music_player.volume = SETTINGS.music_volume * DUCK_FACTOR

    def _create_fade_texture(self):
        fade_width = 256
        image = Image.new("RGBA", (fade_width, 1))
        for x in range(fade_width):
            progress = x / (fade_width - 1)
            alpha = int(164 * (1 - progress) ** 1.9)
            image.putpixel((x, 0), (8, 10, 17, alpha))
        return arcade.Texture(image=image)

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

    def on_draw(self):
        self.game_view.on_draw()

        width = self.window.width
        height = self.window.height
        self.button_hitboxes = []

        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (4, 6, 11, 160))

        fade_width = min(590, width * 0.52)
        arcade.draw_texture_rect(
            self.fade_texture,
            arcade.LBWH(0, 0, fade_width, height),
        )

        cx = self._panel_center_x(width)
        title_y = height - 108

        arcade.draw_text(
            "PAUSA",
            cx,
            title_y,
            self.cream,
            40,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )
        arcade.draw_line(
            cx - 72, title_y - 32,
            cx + 72, title_y - 32,
            (212, 165, 78, 92), 1,
        )

        start_y = height * 0.56
        gap = 62

        for i, (label, _) in enumerate(self.options):
            y = start_y - i * gap
            self._draw_button(i, label, cx, y, i == self.selected_index)

        arcade.draw_text(
            "W S / flechas  ·  Enter  ·  Esc",
            cx,
            52,
            self.muted,
            15,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )

    def _panel_center_x(self, width):
        return min(300, width * 0.2)

    def _draw_button(self, index, label, x, y, selected):
        btn_w = 330
        btn_h = 48
        left = x - btn_w / 2
        right = x + btn_w / 2
        bottom = y - btn_h / 2
        top = y + btn_h / 2

        self.button_hitboxes.append((index, left, right, bottom, top))

        arcade.draw_text(
            label,
            x,
            y,
            (255, 255, 255) if selected else (190, 182, 162),
            32 if selected else 26,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
            bold=selected,
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
        for i, left, right, bottom, top in self.button_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = i
                return

    def on_mouse_press(self, x, y, button, modifiers):
        for i, left, right, bottom, top in self.button_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = i
                self.activate_selected()
                return

    def activate_selected(self):
        _, action = self.options[self.selected_index]
        action()

    def resume_game(self):
        self.window.show_view(self.game_view)

    def open_settings(self):
        self.window.show_view(SettingsView(self))

    def update_music_volume(self):
        if self.game_view.music_player:
            self.game_view.music_player.volume = SETTINGS.music_volume * DUCK_FACTOR

    def go_main_menu(self):
        from views.menu_view import MainMenu
        from views.transitions import FadeToView

        if self.game_view.music_player:
            self.game_view.music_player.delete()
            self.game_view.music_player = None

        self.window.show_view(FadeToView(self, MainMenu, duration=0.7))
