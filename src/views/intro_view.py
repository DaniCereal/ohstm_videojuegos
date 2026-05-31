from pathlib import Path

import arcade
import cv2
from PIL import Image

from data.settings import SETTINGS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"
INTRO_VIDEO_PATHS = [
    ASSETS_ROOT / "mp4" / f"Escena_{index}.mp4"
    for index in range(1, 7)
]
INTRO_MUSIC_PATH = ASSETS_ROOT / "Music" / "OST" / "Initial_Story.mp3"


class IntroStoryView(arcade.View):
    def __init__(self, save_data):
        super().__init__()
        self.save_data = save_data
        self.scene_index = -1
        self.video = None
        self.current_frame_texture = None
        self.frame_time = 1 / 30
        self.frame_accumulator = 0.0
        self.skip_cooldown = 0.0
        self.pending_finish = False
        self.music = None
        self.music_player = None
        self.font_name = "Garamond"

        if INTRO_MUSIC_PATH.exists():
            self.music = arcade.load_sound(str(INTRO_MUSIC_PATH))
            self.music_player = self.music.play(
                volume=SETTINGS.music_volume,
                loop=True,
            )

        self.start_next_scene()

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        if self.pending_finish:
            self.finish_intro()

    def on_draw(self):
        self.clear()
        width = self.window.width
        height = self.window.height

        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), arcade.color.BLACK)

        if self.current_frame_texture:
            video_width = self.current_frame_texture.width
            video_height = self.current_frame_texture.height
            scale = min(width / video_width, height / video_height)
            draw_width = video_width * scale
            draw_height = video_height * scale
            arcade.draw_texture_rect(
                self.current_frame_texture,
                arcade.LBWH(
                    (width - draw_width) / 2,
                    (height - draw_height) / 2,
                    draw_width,
                    draw_height,
                ),
            )

        self.draw_scene_counter(width, height)

    def draw_scene_counter(self, width, height):
        arcade.draw_text(
            f"{self.scene_index + 1}/6",
            width - 34,
            28,
            (224, 218, 202, 150),
            16,
            anchor_x="right",
            anchor_y="center",
            font_name=self.font_name,
        )

    def on_update(self, delta_time):
        if not self.video:
            return

        self.skip_cooldown = max(0.0, self.skip_cooldown - delta_time)
        self.frame_accumulator += delta_time
        if self.frame_accumulator < self.frame_time:
            return

        self.frame_accumulator %= self.frame_time
        self.read_next_frame()

    def on_key_press(self, key, modifiers):
        self.skip_current_scene()

    def on_mouse_press(self, x, y, button, modifiers):
        self.skip_current_scene()

    def skip_current_scene(self):
        if self.skip_cooldown > 0:
            return

        self.skip_cooldown = 0.2
        self.start_next_scene()

    def start_next_scene(self):
        self.release_video()
        self.scene_index += 1
        self.current_frame_texture = None
        self.frame_accumulator = 0.0

        while self.scene_index < len(INTRO_VIDEO_PATHS):
            path = INTRO_VIDEO_PATHS[self.scene_index]
            if not path.exists():
                self.scene_index += 1
                continue

            self.video = cv2.VideoCapture(str(path))
            fps = self.video.get(cv2.CAP_PROP_FPS)
            if fps and fps > 0:
                self.frame_time = 1 / fps
            else:
                self.frame_time = 1 / 30
            self.read_next_frame()
            return

        if getattr(self, "window", None) is None:
            self.pending_finish = True
            return

        self.finish_intro()

    def read_next_frame(self):
        success, frame = self.video.read()
        if not success:
            self.start_next_scene()
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame).convert("RGBA")
        self.current_frame_texture = arcade.Texture(image=image)

    def finish_intro(self):
        self.cleanup()

        from views.game_view import GameView

        game = GameView(
            score=self.save_data["score"],
            lives=self.save_data["lives"],
            max_lives=self.save_data["max_lives"],
            room_position=self.save_data["room"],
            entry_side=self.save_data["entry_side"],
            daedalus_dialogue_complete=self.save_data["daedalus_dialogue_complete"],
            daedalus_second_dialogue_complete=self.save_data["daedalus_second_dialogue_complete"],
            talked_to_zeus=self.save_data["talked_to_zeus"],
            hades_dialogue_complete=self.save_data["hades_dialogue_complete"],
            dialogue_progress=self.save_data["dialogue_progress"],
            feather_count=self.save_data["feather_count"],
            cleared_feather_rooms=self.save_data["cleared_feather_rooms"],
            has_double_jump=self.save_data["has_double_jump"],
            has_dash=self.save_data["has_dash"],
            has_wall_jump=self.save_data["has_wall_jump"],
        )
        self.window.show_view(game)

    def release_video(self):
        if self.video:
            self.video.release()
            self.video = None

    def update_music_volume(self):
        if self.music_player is not None:
            self.music_player.volume = SETTINGS.music_volume

    def cleanup(self):
        self.release_video()

        if self.music_player:
            self.music_player.delete()
            self.music_player = None
