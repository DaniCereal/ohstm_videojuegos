import arcade
import cv2
from PIL import Image
from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data.settings import SETTINGS
from data.savegame import reset_save
from views.credits_view import CreditsView
from views.settings_view import SettingsView

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.video = cv2.VideoCapture(str(ASSETS_ROOT / "mp4" / "Menu_principal.mp4"))
        self.music = arcade.load_sound(str(ASSETS_ROOT / "Music" / "OST" / "MenuPrincipal.ogg"))
        self.music_player = self.music.play(
            volume=SETTINGS.music_volume,
            loop=True,
        )

        self.current_frame_texture = None
        self.font_name = "Garamond"
        self.logo = arcade.load_texture(str(ASSETS_ROOT / "images" / "LogoNoBackground.png"))
        self.fade_texture = self._create_fade_texture()

        self.selected_index = 0
        self.buttons = [
            ("Nueva Partida", self.new_game),
            ("Jugar", self.continue_game),
            ("Ajustes", self.settings),
            ("Creditos", self.credits),
            ("Salir", self.exit_game),
        ]

        self.current_game_view = None

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

    def on_draw(self):
        self.clear()

        width = self.window.width
        height = self.window.height

        if self.current_frame_texture:
            arcade.draw_texture_rect(
                self.current_frame_texture,
                arcade.LBWH(0, 0, width, height),
            )
        else:
            arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (10, 14, 24))

        self._draw_atmosphere(width, height)
        self._draw_menu_panel(width, height)
        self._draw_logo(width, height)
        self._draw_buttons(width, height)

    def _draw_atmosphere(self, width, height):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (7, 10, 18, 74))
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height * 0.18), (34, 20, 24, 60))

    def _draw_menu_panel(self, width, height):
        fade_width = min(590, width * 0.52)
        arcade.draw_texture_rect(
            self.fade_texture,
            arcade.LBWH(0, 0, fade_width, height),
        )

    def _draw_logo(self, width, height):
        center_x = self._menu_center_x(width)
        logo_width = min(width * 0.32, 470)
        logo_height = logo_width * 0.48
        logo_x = center_x - logo_width / 2
        logo_y = height - logo_height - 58

        arcade.draw_texture_rect(
            self.logo,
            arcade.LBWH(logo_x, logo_y, logo_width, logo_height),
        )

    def _draw_buttons(self, width, height):
        start_y = height * 0.56
        gap = 64
        x = self._menu_center_x(width)

        for i, (label, _action) in enumerate(self.buttons):
            y = start_y - i * gap
            self._draw_button(label, x, y, i == self.selected_index)

    def _menu_center_x(self, width):
        return min(300, width * 0.2)

    def _create_fade_texture(self):
        fade_width = 256
        image = Image.new("RGBA", (fade_width, 1))

        for x in range(fade_width):
            progress = x / (fade_width - 1)
            alpha = int(164 * (1 - progress) ** 1.9)
            image.putpixel((x, 0), (8, 10, 17, alpha))

        return arcade.Texture(image=image)

    def _draw_button(self, label, x, y, selected):
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
        if key in (arcade.key.UP, arcade.key.W):
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
        elif key in (arcade.key.ENTER, arcade.key.SPACE):
            self.activate_selected()

    def on_mouse_motion(self, x, y, dx, dy):
        self.selected_index = self.get_button_at(x, y, self.selected_index)

    def on_mouse_press(self, x, y, button, modifiers):
        self.selected_index = self.get_button_at(x, y, self.selected_index)
        self.activate_selected()

    def get_button_at(self, x, y, default):
        start_y = self.window.height * 0.56
        gap = 64
        center_x = self._menu_center_x(self.window.width)
        width = 330
        height = 42

        for i in range(len(self.buttons)):
            option_y = start_y - i * gap
            left = center_x - width / 2
            right = center_x + width / 2
            bottom = option_y - height / 2
            top = option_y + height / 2

            if left <= x <= right and bottom <= y <= top:
                return i

        return default

    def activate_selected(self):
        _label, action = self.buttons[self.selected_index]
        action()

    def new_game(self):
        self.stop_menu_media()

        from views.intro_view import IntroStoryView

        save_data = reset_save()
        intro = IntroStoryView(save_data)
        self.window.show_view(intro)

    def continue_game(self):
        self.stop_menu_media()

        from views.game_view import GameView

        game = GameView(load_from_save=True)
        self.current_game_view = game
        self.window.show_view(game)

    def settings(self):
        self.window.show_view(SettingsView(self))

    def story(self):
        print("Historia")

    def credits(self):
        self.window.show_view(CreditsView(self))

    def exit_game(self):
        self.stop_menu_media()
        arcade.exit()

    def on_update(self, delta_time):
        success, frame = self.video.read()
        if not success:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.video.read()

        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame).convert("RGBA")
            self.current_frame_texture = arcade.Texture(image=image)

    def stop_menu_media(self):
        if self.video:
            self.video.release()

        if self.music_player:
            self.music_player.pause()

    def update_music_volume(self):
        if self.music_player is not None:
            self.music_player.volume = SETTINGS.music_volume

    def cleanup(self):
        if self.video:
            self.video.release()

        if self.music_player:
            self.music_player.pause()
            self.music_player = None
