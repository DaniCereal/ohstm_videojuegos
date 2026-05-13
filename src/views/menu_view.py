import arcade

from constants import *
from views.settings_view import SettingsView

import cv2
import arcade

from PIL import Image

from data.settings import SETTINGS

class MainMenu(arcade.View):

    def __init__(self):

        super().__init__()

        # TEXTURAS PLACEHOLDER


        video_path = "../assets/mp4/Menu_principal.mp4"

        self.video = cv2.VideoCapture(video_path)

        self.music = arcade.load_sound(
            "../assets/Music/OST/MenuPrincipal.ogg"
        )

        self.music_player = self.music.play(
            volume=SETTINGS.music_volume,
            loop=True
        )

        self.current_frame_texture = None

        self.logo = arcade.load_texture(
            "../assets/images/LogoNoBackground.png"
        )

        

        # BOTONES

        self.selected_index = 0

        self.buttons = [

            ("Nueva Partida", self.new_game),

            ("Jugar", self.continue_game),

            ("Historia", self.story),

            ("Ajustes", self.settings),

            ("Créditos", self.credits),

            ("Salir", self.exit_game),
        ]

        # Guarda partida actual
        self.current_game_view = None

    # DRAW

    def on_draw(self):

        self.clear()

        screen_width = self.window.width
        screen_height = self.window.height

        # FONDO

        if self.current_frame_texture:
            arcade.draw_texture_rect(
                self.current_frame_texture,
                arcade.LBWH(
                    0,
                    0,
                    screen_width,
                    screen_height
                )
            )

        # Oscurecer un poco
        arcade.draw_rect_filled(
            arcade.LBWH(
                0,
                0,
                screen_width,
                screen_height
            ),
            (0, 0, 0, 120)
        )

        # LOGO

        logo_width = screen_width * 0.32
        logo_height = logo_width * 0.48

        arcade.draw_texture_rect(
            self.logo,
            arcade.LBWH(
                30,
                screen_height - logo_height - 80,
                logo_width,
                logo_height
            )
        )

        # BOTONES

        start_y = screen_height * 0.55

        gap = 70

        x = 250

        for i, (label, _) in enumerate(self.buttons):

            y = start_y - i * gap

            selected = i == self.selected_index

            # Fondo botón seleccionado
            if selected:

                arcade.draw_rect_filled(
                    arcade.LRBT(
                        x - 170,
                        x + 170,
                        y - 25,
                        y + 25
                    ),
                    (255, 255, 255, 40)
                )

            arcade.draw_text(
                label,
                x,
                y,
                arcade.color.WHITE
                if not selected
                else arcade.color.GOLD,
                28,
                anchor_x="center",
                anchor_y="center"
            )

        # TEXTO ABAJO

        arcade.draw_text(
            "↑ ↓  ·  ENTER",
            screen_width - 120,
            30,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )

    # INPUT

    def on_key_press(self, key, modifiers):

        if key in (arcade.key.UP, arcade.key.W):

            self.selected_index -= 1

            if self.selected_index < 0:
                self.selected_index = len(self.buttons) - 1

        elif key in (arcade.key.DOWN, arcade.key.S):

            self.selected_index += 1

            if self.selected_index >= len(self.buttons):
                self.selected_index = 0

        elif key in (arcade.key.ENTER, arcade.key.SPACE):

            self.activate_selected()

    def on_mouse_motion(self, x, y, dx, dy):

        self.selected_index = self.get_button_at(
            x,
            y,
            self.selected_index
        )

    def on_mouse_press(self, x, y, button, modifiers):

        self.selected_index = self.get_button_at(
            x,
            y,
            self.selected_index
        )

        self.activate_selected()

    # BOTONES

    def get_button_at(self, x, y, default):

        start_y = self.window.height * 0.55

        gap = 70

        center_x = 250

        width = 340

        height = 50

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

        _, action = self.buttons[self.selected_index]

        action()

    # ACCIONES

    def new_game(self):
        self.stop_menu_media()

        from views.game_view import GameView

        game = GameView()

        game.setup()

        self.current_game_view = game

        self.window.show_view(game)

    def continue_game(self):
        self.stop_menu_media()

        if self.current_game_view:

            self.window.show_view(
                self.current_game_view
            )

        else:

            self.new_game()

    def settings(self):
        self.window.show_view(SettingsView(self))

    def story(self):

        print("Historia")

    def credits(self):

        print("Créditos")

    def exit_game(self):
        self.stop_menu_media()
        arcade.exit()

    def on_update(self, delta_time):

        success, frame = self.video.read()

        # Reiniciar vídeo cuando termina
        if not success:

            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)

            success, frame = self.video.read()

        if success:

            # Convertir BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            height, width, _ = frame.shape

            image = Image.fromarray(frame).convert("RGBA")

            self.current_frame_texture = arcade.Texture(
                image=image
            )
            
    def stop_menu_media(self):
        if self.video:
            self.video.release()

        if self.music_player:
            self.music_player.pause()

    def update_music_volume(self):

        if self.music_player:

            self.music_player.volume = SETTINGS.music_volume

    def cleanup(self):
        if self.video:
            self.video.release()

        if self.music_player:
            self.music_player.pause()
            self.music_player = None
    
    def on_show_view(self):
        self.window.ctx.viewport = (
            0,
            0,
            self.window.width,
            self.window.height
        )
    
    def update_music_volume(self):
        if self.music_player is not None:
            self.music_player.volume = SETTINGS.music_volume