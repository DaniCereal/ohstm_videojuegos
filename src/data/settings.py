import arcade
import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "settings.json"

class GameSettings:
    def __init__(self):

        # --- AUDIO ---
        self.music_volume = 0.5
        self.voice_volume = 0.5
        self.sfx_volume = 0.7

        # --- VIDEO ---
        self.fullscreen = False

        # --- CONTROLS ---
        self.key_up = arcade.key.W
        self.key_down = arcade.key.S
        self.key_left = arcade.key.A
        self.key_right = arcade.key.D

        self.key_dash = arcade.key.LSHIFT
        self.key_pause = arcade.key.ESCAPE
        self.key_restart = arcade.key.R

    def save(self):

        data = {
            "music_volume": self.music_volume,
            "voice_volume": self.voice_volume,
            "sfx_volume": self.sfx_volume,
            "fullscreen": self.fullscreen,

            "key_up": self.key_up,
            "key_down": self.key_down,
            "key_left": self.key_left,
            "key_right": self.key_right,

            "key_dash": self.key_dash,
            "key_pause": self.key_pause,
            "key_restart": self.key_restart,
        }

        with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self):

        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.music_volume = data["music_volume"]
            self.voice_volume = data["voice_volume"]
            self.sfx_volume = data["sfx_volume"]

            self.fullscreen = data["fullscreen"]

            self.key_up = data["key_up"]
            self.key_down = data["key_down"]
            self.key_left = data["key_left"]
            self.key_right = data["key_right"]

            self.key_dash = data["key_dash"]
            self.key_pause = data["key_pause"]
            self.key_restart = data["key_restart"]

        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            self.save()


SETTINGS = GameSettings()
