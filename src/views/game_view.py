import arcade
import math
import random
import textwrap
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from data.savegame import (
    DEFAULT_ENTRY_SIDE,
    DEFAULT_ROOM,
    MAX_LIVES,
    load_save,
    save_game
)
from data.settings import SETTINGS

from constants import *

from models.player import PlayerCharacter

from models.enemy import (
    RobotEnemy,
    ZombieEnemy
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"

LEVEL_FILES = {
    (2, 0): "2-0.tmx",
    (2, 1): "2-1.tmx",
    (2, 2): "2-2.tmx",
    (2, 3): "2-3.tmx",
    (2, 4): "2-4.tmx",
    (2, 5): "2-5.tmx",
    (2, 6): "2-6.tmx",
    (2, 7): "2-7.tmx",
    (1, 1): "1-1.tmx",
    (1, 2): "1-2.tmx",
    (1, 3): "1-3.tmx",
    (0, 3): "0_3.tmx",
    (0, 2): "0_2.tmx",
    (0, 1): "0-1.tmx",
    (1, 4): "1-4.tmx",
    (1, 5): "1-5.tmx",
    (0, 4): "0-4.tmx",
    (0, 5): "0-5.tmx",
    (0, 6): "0-6.tmx",
    (0, 7): "0-7.tmx",
    (3, 2): "3-2.tmx",
    (3, 3): "3-3.tmx",
    (3, 4): "3-4.tmx",
    (4, 4): "4-4.tmx",
    (3, 5): "3-5.tmx",
    (3, 6): "3-6.tmx",
    (4, 5): "4-5.tmx",
    (5, 5): "5-5.tmx",
    (5, 6): "5-6.tmx",
    (5, 7): "5-7.tmx",
    (4, 7): "4-7.tmx",
    (5, 4): "5-4.tmx",
    (5, 3): "5-3.tmx",
    (4, 3): "4-3.tmx",
    (4, 2): "4-2.tmx",
}
LEVEL_GRID = {
    room: ASSETS_ROOT / "Niveles" / filename
    for room, filename in LEVEL_FILES.items()
    if (ASSETS_ROOT / "Niveles" / filename).exists()
}
LEVEL_ORDER = tuple(room for room in LEVEL_FILES if room in LEVEL_GRID)
LEVELS = [LEVEL_GRID[position] for position in LEVEL_ORDER]

LEVEL_MUSIC = [ASSETS_ROOT / "Music" / "OST" / "Earth_1_clean.wav"] * len(LEVEL_ORDER)

# Todas las salas de fila 0 y 1 son Olimpo
OVERWORLD_ROOMS = frozenset({
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
})
OVERWORLD_MUSIC = [
    ASSETS_ROOT / "Music" / "OST" / "Olympus_1_clean.wav",
    ASSETS_ROOT / "Music" / "OST" / "Olympus_2_clean.wav",
]

# Filas 3-4 → Inframundo 1, fila 5 → Inframundo 2
UNDERWORLD_1_ROOMS = frozenset({
    (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
    (4, 2), (4, 3), (4, 4), (4, 5), (4, 7),
})
UNDERWORLD_2_ROOMS = frozenset({
    (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
})
UNDERWORLD_1_MUSIC = ASSETS_ROOT / "Music" / "OST" / "Underworld_1_clean.wav"
UNDERWORLD_2_MUSIC = ASSETS_ROOT / "Music" / "OST" / "Underworld_2_clean.wav"

OPPOSITE_SIDE = {
    "left": "right",
    "right": "left",
    "top": "bottom",
    "bottom": "top",
}

ROOM_CONNECTIONS = {
    (2, 0): {
        "right": (2, 1),
    },
    (2, 1): {
        "right": (2, 2),
        "left": (2, 0),
        "top": (1, 1),
    },
    (2, 2): {
        "left": (2, 1),
        "right": (2, 3),
        "top": (1, 2),
        "bottom": (3, 2),
    },
    (2, 3): {
        "left": (2, 2),
        "right": (2, 4),
    },
    (2, 4): {
        "left": (2, 3),
        "right": (2, 5),
        "top": (1, 4),
    },
    (2, 5): {
        "left": (2, 4),
        "right": (2, 6),
    },
    (2, 6): {
        "left": (2, 5),
        "right": (2, 7),
    },
    (2, 7): {
        "left": (2, 6),
    },
    (1, 1): {
        "bottom": (2, 1),
    },
    (1, 2): {
        "bottom": (2, 2),
        "right": (1, 3),
    },
    (1, 3): {
        "left": (1, 2),
        "top": (0, 3),
    },
    (0, 3): {
        "bottom": (1, 3),
        "left": (0, 2),
    },
    (0, 2): {
        "right": (0, 3),
        "left": (0, 1),
    },
    (0, 1): {
        "right": (0, 2),
    },
    (1, 4): {
        "bottom": (2, 4),
        "right": (1, 5),
        "top": (0, 4),
    },
    (1, 5): {
        "left": (1, 4),
    },
    (0, 4): {
        "bottom": (1, 4),
        "right": (0, 5),
    },
    (0, 5): {
        "left": (0, 4),
        "right": (0, 6),
    },
    (0, 6): {
        "left": (0, 5),
        "right": (0, 7),
    },
    (0, 7): {
        "left": (0, 6),
    },
    (3, 2): {
        "top": (2, 2),
        "right": (3, 3),
    },
    (3, 3): {
        "left": (3, 2),
        "right": (3, 4),
    },
    (3, 4): {
        "left": (3, 3),
        "right": (3, 5),
        "bottom": (4, 4),
    },
    (4, 4): {
        "top": (3, 4),
    },
    (3, 5): {
        "left": (3, 4),
        "right": (3, 6),
        "bottom": (4, 5),
    },
    (3, 6): {
        "left": (3, 5),
    },
    (4, 5): {
        "top": (3, 5),
        "bottom": (5, 5),
    },
    (5, 5): {
        "top": (4, 5),
        "right": (5, 6),
        "left": (5, 4),
    },
    (5, 6): {
        "left": (5, 5),
        "right": (5, 7),
    },
    (5, 7): {
        "left": (5, 6),
        "top": (4, 7),
    },
    (4, 7): {
        "bottom": (5, 7),
    },
    (5, 4): {
        "left": (5, 3),
        "right": (5, 5),
    },
    (5, 3): {
        "right": (5, 4),
        "top": (4, 3),
    },
    (4, 3): {
        "bottom": (5, 3),
        "left": (4, 2),
    },
    (4, 2): {
        "right": (4, 3),
    },
}

SAFE_ROOMS = {(1, 1), (1, 5), (4, 4)}

SIDE_EXIT_MARGIN = 1
FALL_VOID_MARGIN = 20

FEATHER_NORMAL_PATH = ASSETS_ROOT / "Sprites" / "Feathers" / "white_feather.png"
FEATHER_GOLDEN_PATH = ASSETS_ROOT / "Sprites" / "Feathers" / "golden_feather.png"
FEATHER_BLUE_PATH   = ASSETS_ROOT / "Sprites" / "Feathers" / "blue_timer_feather.png"
FEATHER_GOLDEN_VALUE       = 5

# Tiendas de habilidades: sala → {tipo, coste, nombre}
ABILITY_SHOPS = {
    (0, 1): {"type": "life",        "cost": 12, "label": "una Vida extra"},
    (0, 7): {"type": "life",        "cost": 12, "label": "una Vida extra"},
    (2, 7): {"type": "life",        "cost": 12, "label": "una Vida extra"},
    (3, 3): {"type": "wall_jump",   "cost": 18, "label": "Salto en Pared"},
    (4, 7): {"type": "double_jump", "cost": 18, "label": "Doble Salto"},
    (0, 6): {"type": "dash",        "cost": 12, "label": "Dash"},
}
SHOP_INTERACT_DISTANCE = 90
FEATHER_BLUE_TIMER         = 13.0
FEATHER_BLUE_REWARD        = 5
FEATHER_NORMAL_COUNT       = 5
FEATHER_GOLDEN_PROB        = 0.08
FEATHER_BLUE_TRAIL_COUNT   = 7
FEATHER_BLUE_PENALTY       = 3
BLUE_MUSIC_DUCK            = 0.55


def _make_tick_wav():
    import wave, struct, math as _m
    path = ASSETS_ROOT / "Music" / "SE" / "tick.wav"
    if not path.exists():
        sr, freq, dur = 44100, 950, 0.055
        frames = b"".join(
            struct.pack("<h", int(32767 * _m.exp(-i / sr * 45) * _m.sin(2 * _m.pi * freq * i / sr)))
            for i in range(int(sr * dur))
        )
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(frames)
    return path


TICK_SOUND_PATH = _make_tick_wav()

DAEDALUS_ROOM = (2, 1)
DAEDALUS_POSITION = (255, 170)
ZEUS_ROOM = (0, 2)
ZEUS_POSITION = (95, 520)
DIALOGUE_INTERACT_DISTANCE = 96
DIALOGUE_PATH = PROJECT_ROOT / "docs" / "Dialogues" / "DedaloFirstTimeMeet"
DEDALO_VOICE_DIR = PROJECT_ROOT / "assets" / "VSX" / "Dedalo"
HERMES_SPEAKING_DIR = PROJECT_ROOT / "assets" / "VSX" / "Hermes" / "HermesSpeaking"
HERMES_MOVEMENT_DIR = PROJECT_ROOT / "assets" / "VSX" / "Hermes" / "Movement"
SPAWN_OBJECT_LAYER_NAMES = ("Spawns", "Spawn", "PlayerSpawns", "Player Spawns")

PLATFORM_LAYER_CANDIDATES = (
    "Platforms",
    "Capa de patrones 1",
    "Ruta Uno",
)

# Capas del TMX que NO son sólidas (no se usan para colisión de plumas)
_NONSOLD_LAYERS = frozenset({
    "Enemies", "Coins", "NPCs", "Feathers", "Spawns", "Spawn",
    "PlayerSpawns", "Player Spawns", "Ladders", "Moving Platforms",
    "Backgrounds", "Background", "Decorations", "Decoration", "Fondo",
})

class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(
        self,
        level=1,
        score=0,
        lives=MAX_LIVES,
        room_position=None,
        entry_side=DEFAULT_ENTRY_SIDE,
        load_from_save=False,
        inherited_music=None,
        inherited_music_player=None,
        daedalus_dialogue_complete=False,
        inherited_overworld_track_index=0,
        feather_count=0,
        cleared_feather_rooms=None,
        has_double_jump=False,
        has_dash=False,
        has_wall_jump=False,
    ):
        self.last_wall_touched = 0

        # Call the parent class and set up the window
        super().__init__()

        if load_from_save:
            save_data = load_save()
            if save_data["has_checkpoint"]:
                room_position = save_data["room"]
                entry_side = save_data["entry_side"]
                score = save_data["score"]
                daedalus_dialogue_complete = save_data["daedalus_dialogue_complete"]
                feather_count = save_data["feather_count"]
                cleared_feather_rooms = save_data.get("cleared_feather_rooms", [])
                has_double_jump = save_data.get("has_double_jump", False)
                has_dash = save_data.get("has_dash", False)
                has_wall_jump = save_data.get("has_wall_jump", False)
            else:
                room_position = DEFAULT_ROOM
                entry_side = DEFAULT_ENTRY_SIDE
                score = 0
                daedalus_dialogue_complete = False
                feather_count = 0
                cleared_feather_rooms = []
                has_double_jump = False
                has_dash = False
                has_wall_jump = False
            lives = MAX_LIVES

        if room_position is None:
            room_position = self.room_from_level(level)

        if tuple(room_position) not in LEVEL_GRID:
            room_position = DEFAULT_ROOM

        if entry_side not in OPPOSITE_SIDE:
            entry_side = DEFAULT_ENTRY_SIDE

        self.current_room = tuple(room_position)
        self.level = self.level_from_room(self.current_room)
        self.entry_side = entry_side
        self.initialized = False

        # Track the current state of our input
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_queued = False
        self.touching_left_wall = False
        self.touching_right_wall = False
        self.wall_jump_wall_direction = 0

        # Variable to hold our texture for our player
        self.player_texture = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable to hold our Tiled Map
        self.tile_map = None

        # Replacing all of our SpriteLists with a Scene variable
        self.scene = None
        self.platform_sprites = None
        self.moving_platform_sprites = None
        self.ladder_sprites = None
        self.enemy_sprites = None
        self.coin_sprites = None
        self.npc_sprites = None
        self.reset_sprites = None
        self.feather_count = feather_count
        self.cleared_feather_rooms = set(tuple(r) for r in (cleared_feather_rooms or []))
        self.has_double_jump = has_double_jump
        self.has_dash = has_dash
        self.has_wall_jump = has_wall_jump
        self.shop_sprite = None
        self.shop_data = None
        self.feather_sprites_normal = arcade.SpriteList()
        self.feather_sprites_golden = arcade.SpriteList()
        self.feather_sprites_blue = arcade.SpriteList()
        self._blue_trail_sprites = arcade.SpriteList()
        self._tex_blue = None
        self._solid_sprite_lists = []
        self.blue_timer_active = False
        self.blue_timer_remaining = 0.0
        self.blue_trail_total = 0
        self._feather_hud_texture = None
        self._tick_sound = arcade.load_sound(str(TICK_SOUND_PATH))
        self._tick_timer = 0.0
        self.daedalus_npc = None
        self.daedalus_textures = []
        self.daedalus_anim_timer = 0
        self.zeus_npc = None
        self.zeus_textures = []
        self.zeus_anim_timer = 0
        self.overworld_track_index = inherited_overworld_track_index

        # A variable to store our camera object
        self.camera = None

        # A variable to store our gui camera object
        self.gui_camera = None

        # This variable will store our score as an integer.
        self.score = score
        self.lives = lives

        # This variable will store the text for score that we will draw to the screen.
        self.score_text = None
        self.lives_text = None

        # Where is the right edge of the map?
        self.end_of_map = 0
        self.map_width = 0
        self.map_height = 0

        # Should we reset the score?
        self.reset_score = False

        # Music (puede heredarse de la sala anterior si es el mismo track)
        self.music = inherited_music
        self.music_player = inherited_music_player
        self.dialogue_lines = []
        self.active_dialogue_lines = []
        self.dialogue_active = False
        self.dialogue_index = 0
        self.daedalus_dialogue_complete = daedalus_dialogue_complete
        self.voice_player = None
        self.voice_sounds = {}
        self.hermes_movement_sounds = []

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        _death_wav = ASSETS_ROOT / "VSX" / "Hermes" / "HermesDeath.wav"
        self.gameover_voice = arcade.load_sound(_death_wav) if _death_wav.exists() else None
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

    @staticmethod
    def room_from_level(level):
        try:
            return LEVEL_ORDER[level - 1]
        except IndexError:
            return DEFAULT_ROOM

    @staticmethod
    def level_from_room(room):
        if room in LEVEL_ORDER:
            return LEVEL_ORDER.index(room) + 1

        return 1

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        layer_options = {
            "Moving Platforms": {
                "use_spatial_hash": False
            },
            "Ladders": {
                "use_spatial_hash": True
            }
        }
        for layer_name in PLATFORM_LAYER_CANDIDATES:
            layer_options[layer_name] = {"use_spatial_hash": True}

        map_path = LEVEL_GRID[self.current_room]
        self.map_path = Path(map_path)

        self.tile_map = arcade.load_tilemap(
            str(map_path),
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Create our Scene Based on the TileMap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.platform_sprites = self.find_platform_sprites()
        self.enemy_sprites = self.ensure_sprite_list("Enemies")
        self.coin_sprites = self.ensure_sprite_list("Coins")
        self.moving_platform_sprites = self.ensure_sprite_list("Moving Platforms")
        self.ladder_sprites = self.ensure_sprite_list("Ladders")
        self.npc_sprites = self.ensure_sprite_list("NPCs")
        self.reset_sprites = self.build_reset_sprites()
        self.calculate_map_bounds()
        self.load_voice_assets()

        self.player_sprite = PlayerCharacter()
        self.load_feather_sprites()
        self.apply_feather_unlocks()



        self.place_player_at_entry()
        self.scene.add_sprite("Player", self.player_sprite)

        # -- Enemies
        if "Enemies" in self.tile_map.object_lists:
            enemies_layer = self.tile_map.object_lists["Enemies"]

            for enemy_marker in enemies_layer:
                enemy_properties = enemy_marker.properties or {}

                coordinates = self.tile_map.get_cartesian(
                    enemy_marker.shape[0],
                    enemy_marker.shape[1]
                )

                enemy_type = enemy_properties.get("type", "zombie")

                if enemy_type == "robot":
                    enemy = RobotEnemy()

                elif enemy_type == "zombie":
                    enemy = ZombieEnemy()
                else:
                    enemy = ZombieEnemy()

                enemy.center_x = math.floor(
                    coordinates[0]
                    * TILE_SCALING
                    * self.tile_map.tile_width
                )

                enemy.center_y = math.floor(
                    (coordinates[1] + 1)
                    * (self.tile_map.tile_height * TILE_SCALING)
                )

                enemy.boundary_left = float(
                    enemy_properties.get("boundary_left", enemy.center_x - 150)
                )
                enemy.boundary_right = float(
                    enemy_properties.get("boundary_right", enemy.center_x + 150)
                )
                enemy.change_x = float(
                    enemy_properties.get("change_x", enemy.change_x)
                )

                self.scene.add_sprite("Enemies", enemy)

        self.add_room_npcs()
        self._setup_shop()

        # Create a Platformer Physics Engine, this will handle moving our
        # player as well as collisions between the player sprite and
        # whatever SpriteList we specify for the walls.
        # It is important to supply static to the walls parameter. There is a
        # platforms parameter that is intended for moving platforms.
        # If a platform is supposed to move, and is added to the walls list,
        # it will not be moved.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.platform_sprites,
            gravity_constant=GRAVITY,
            platforms=self.moving_platform_sprites,
            ladders=self.ladder_sprites
        )

        self.camera = arcade.camera.Camera2D()

        self.camera.viewport = arcade.LRBT(
            0,
            self.window.width,
            0,
            self.window.height
        )

        self.gui_camera = arcade.camera.Camera2D()

        self.score_text = None
        self.lives_text = None

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        if self.tile_map.background_color:
            self.window.background_color = self.tile_map.background_color
        else:
            self.window.background_color = arcade.color.BLACK

        if not self.music_player:
            self.start_music()
        self.activate_safe_room_checkpoint()
        self.initialized = True

    def ensure_sprite_list(self, name):
        if name not in self.scene:
            self.scene.add_sprite_list(name)

        return self.scene[name]

    def find_platform_sprites(self):
        for layer_name in PLATFORM_LAYER_CANDIDATES:
            if layer_name in self.scene:
                return self.scene[layer_name]

        self.scene.add_sprite_list("Platforms")
        return self.scene["Platforms"]

    def build_reset_sprites(self):
        reset_sprites = arcade.SpriteList(use_spatial_hash=True)
        reset_hitboxes = self.reset_tile_hitboxes()
        if not reset_hitboxes:
            return reset_sprites

        try:
            root = ET.parse(self.map_path).getroot()
        except (ET.ParseError, OSError):
            return reset_sprites

        tile_width = int(root.attrib["tilewidth"])
        tile_height = int(root.attrib["tileheight"])
        map_height = int(root.attrib["height"])

        for layer in root.findall("layer"):
            if layer.attrib.get("name") not in PLATFORM_LAYER_CANDIDATES:
                continue

            data = layer.find("data")
            if data is None or data.attrib.get("encoding") != "csv":
                continue

            gids = [
                int(value.strip()) & 0x1FFFFFFF
                for value in data.text.split(",")
                if value.strip()
            ]

            for index, gid in enumerate(gids):
                if gid not in reset_hitboxes:
                    continue

                column = index % int(layer.attrib["width"])
                row = index // int(layer.attrib["width"])
                self.remove_platform_sprite_at_tile(
                    column,
                    row,
                    tile_width,
                    tile_height,
                    map_height
                )

                for hitbox in reset_hitboxes[gid]:
                    object_x, object_y, object_width, object_height = hitbox
                    sprite = arcade.SpriteSolidColor(
                        max(1, int(object_width * TILE_SCALING)),
                        max(1, int(object_height * TILE_SCALING)),
                        center_x=(
                            column * tile_width
                            + object_x
                            + object_width / 2
                        ) * TILE_SCALING,
                        center_y=(
                            map_height * tile_height
                            - (
                                row * tile_height
                                + object_y
                                + object_height / 2
                            )
                        ) * TILE_SCALING,
                        color=(255, 0, 0, 0),
                    )
                    reset_sprites.append(sprite)

        return reset_sprites

    def remove_platform_sprite_at_tile(
        self,
        column,
        row,
        tile_width,
        tile_height,
        map_height,
    ):
        center_x = (column + 0.5) * tile_width * TILE_SCALING
        center_y = (map_height - row - 0.5) * tile_height * TILE_SCALING

        for sprite in list(self.platform_sprites):
            if (
                abs(sprite.center_x - center_x) <= 1
                and abs(sprite.center_y - center_y) <= 1
            ):
                sprite.remove_from_sprite_lists()
                return

    def reset_tile_hitboxes(self):
        try:
            root = ET.parse(self.map_path).getroot()
        except (ET.ParseError, OSError):
            return {}

        reset_hitboxes = {}
        for tileset in root.findall("tileset"):
            first_gid = int(tileset.attrib["firstgid"])
            source = tileset.attrib.get("source")
            tileset_root = tileset

            if source:
                tileset_path = self.map_path.parent / source
                try:
                    tileset_root = ET.parse(tileset_path).getroot()
                except (ET.ParseError, OSError):
                    continue

            for tile in tileset_root.findall("tile"):
                tile_type = tile.attrib.get("type", "")
                if tile_type.lower() == "reset":
                    gid = first_gid + int(tile.attrib["id"])
                    hitboxes = []
                    object_group = tile.find("objectgroup")

                    if object_group is not None:
                        for hitbox_object in object_group.findall("object"):
                            hitboxes.append(
                                (
                                    float(hitbox_object.attrib.get("x", 0)),
                                    float(hitbox_object.attrib.get("y", 0)),
                                    float(hitbox_object.attrib.get("width", 0)),
                                    float(hitbox_object.attrib.get("height", 0)),
                                )
                            )

                    if hitboxes:
                        reset_hitboxes[gid] = hitboxes

        return reset_hitboxes

    def load_voice_assets(self):
        self.dialogue_lines = self.load_dialogue(DIALOGUE_PATH)
        self.voice_sounds = {
            "dedalo": self.load_sound_folder(DEDALO_VOICE_DIR),
            "hermes": self.load_sound_folder(HERMES_SPEAKING_DIR),
        }
        self.hermes_movement_sounds = self.load_sound_folder(HERMES_MOVEMENT_DIR)

    @staticmethod
    def load_sound_folder(folder_path):
        if not folder_path.exists():
            return []

        sound_paths = sorted(
            folder_path.glob("*.mp3"),
            key=GameView.natural_path_key,
        )
        return [arcade.load_sound(str(path)) for path in sound_paths]

    @staticmethod
    def natural_path_key(path):
        stem = path.stem
        digits = "".join(character for character in stem if character.isdigit())
        return int(digits) if digits else stem

    @staticmethod
    def normalize_speaker(speaker):
        if not speaker:
            return ""

        text = unicodedata.normalize("NFKD", speaker)
        text = "".join(character for character in text if not unicodedata.combining(character))
        return text.lower().strip()

    @staticmethod
    def load_dialogue(dialogue_path):
        if not dialogue_path.exists():
            return []

        lines = []
        current_speaker = None
        current_text = []

        def flush_current_line():
            nonlocal current_text
            if current_text:
                lines.append(
                    {
                        "speaker": current_speaker,
                        "text": " ".join(current_text).strip(),
                    }
                )
                current_text = []

        for raw_line in dialogue_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                flush_current_line()
                current_speaker = None
                continue

            if line.endswith(":") and len(line) <= 32:
                flush_current_line()
                current_speaker = line[:-1].strip()
            else:
                current_text.append(line)

        flush_current_line()
        return lines

    def add_room_npcs(self):
        if self.current_room == DAEDALUS_ROOM:
            sheet = arcade.load_spritesheet(
                ASSETS_ROOT / "Sprites" / "Dedalo" / "dedalo_sprite_final.png"
            )
            self.daedalus_textures = sheet.get_texture_grid((32, 32), columns=3, count=7)
            self.daedalus_anim_timer = 0

            self.daedalus_npc = arcade.Sprite(scale=2.1)
            self.daedalus_npc.texture = self.daedalus_textures[0]
            self.daedalus_npc.center_x = DAEDALUS_POSITION[0]
            self.daedalus_npc.center_y = 400
            for _ in range(400):
                self.daedalus_npc.center_y -= 1
                if arcade.check_for_collision_with_list(self.daedalus_npc, self.platform_sprites):
                    self.daedalus_npc.center_y += 1
                    break
            self.scene.add_sprite("NPCs", self.daedalus_npc)

        elif self.current_room == ZEUS_ROOM:
            sheet = arcade.load_spritesheet(
                ASSETS_ROOT / "Sprites" / "Zeus" / "zeus_final_final.png"
            )
            self.zeus_textures = sheet.get_texture_grid((32, 32), columns=3, count=12)
            self.zeus_anim_timer = 0

            self.zeus_npc = arcade.Sprite(scale=2.4)
            self.zeus_npc.texture = self.zeus_textures[0]
            self.zeus_npc.center_x = ZEUS_POSITION[0]
            self.zeus_npc.center_y = ZEUS_POSITION[1]
            for _ in range(ZEUS_POSITION[1]):
                self.zeus_npc.center_y -= 1
                if arcade.check_for_collision_with_list(self.zeus_npc, self.platform_sprites):
                    self.zeus_npc.center_y += 1
                    break
            self.scene.add_sprite("NPCs", self.zeus_npc)

    def can_talk_to_daedalus(self):
        if not self.daedalus_npc:
            return False

        distance = math.hypot(
            self.player_sprite.center_x - self.daedalus_npc.center_x,
            self.player_sprite.center_y - self.daedalus_npc.center_y,
        )
        return distance <= DIALOGUE_INTERACT_DISTANCE

    def start_daedalus_dialogue(self):
        if not self.dialogue_lines:
            return

        if self.daedalus_dialogue_complete:
            self.active_dialogue_lines = [self.dialogue_lines[-1]]
        else:
            self.active_dialogue_lines = self.dialogue_lines

        self.dialogue_active = True
        self.dialogue_index = 0
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        self.play_current_dialogue_voice()

    def advance_dialogue(self):
        if not self.dialogue_active:
            return

        self.dialogue_index += 1
        if self.dialogue_index >= len(self.active_dialogue_lines):
            self.dialogue_active = False
            self.daedalus_dialogue_complete = True
            self.stop_dialogue_voice()
            return

        self.play_current_dialogue_voice()

    def current_dialogue_line(self):
        if not self.dialogue_active:
            return None

        return self.active_dialogue_lines[self.dialogue_index]

    def play_current_dialogue_voice(self):
        line = self.current_dialogue_line()
        if not line:
            return

        self.stop_dialogue_voice()
        speaker = self.normalize_speaker(line["speaker"])
        sounds = self.voice_sounds.get(speaker, [])
        if not sounds:
            return

        self.voice_player = arcade.play_sound(
            random.choice(sounds),
            volume=SETTINGS.voice_volume,
        )

    def stop_dialogue_voice(self):
        if not self.voice_player:
            return

        self.voice_player.delete()
        self.voice_player = None

    def maybe_play_movement_voice(self):
        if not self.hermes_movement_sounds:
            return

        if random.randint(1, 10) != 1:
            return

        arcade.play_sound(
            random.choice(self.hermes_movement_sounds),
            volume=SETTINGS.voice_volume,
        )

    def calculate_map_bounds(self):
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width)
        self.end_of_map *= self.tile_map.scaling
        self.map_width = self.end_of_map
        self.map_height = (
            self.tile_map.height
            * self.tile_map.tile_height
            * self.tile_map.scaling
        )

    def place_player_at_entry(self):
        margin = 96
        tiled_spawn = self.spawn_from_tiled()
        if tiled_spawn:
            self.player_sprite.center_x, self.player_sprite.center_y = tiled_spawn
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.resolve_spawn_collision(margin)
            return

        center_y = max(margin, min(128, self.map_height - margin))

        if self.entry_side == "right":
            self.player_sprite.center_x = self.map_width - margin
            self.player_sprite.center_y = center_y
        elif self.entry_side == "top":
            self.player_sprite.center_x = margin
            self.player_sprite.center_y = self.map_height - margin
        elif self.entry_side == "bottom":
            self.player_sprite.center_x = margin
            self.player_sprite.center_y = margin
        else:
            self.player_sprite.center_x = margin
            self.player_sprite.center_y = center_y

        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        self.resolve_spawn_collision(margin)

    def resolve_spawn_collision(self, margin):
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        self.resolve_sprite_position(
            self.player_sprite,
            start_x,
            start_y,
            prefer_floor=True,
            search_margin=margin / 2,
        )

    def resolve_sprite_position(
        self,
        sprite,
        start_x,
        start_y,
        prefer_floor=False,
        search_margin=48,
    ):
        x_candidates = self.spawn_x_candidates(start_x, search_margin)
        y_candidates = self.spawn_y_candidates(start_y, search_margin)
        free_candidates = []
        supported_candidates = []

        for x in x_candidates:
            for y in y_candidates:
                sprite.center_x = x
                sprite.center_y = y
                if arcade.check_for_collision_with_list(sprite, self.platform_sprites):
                    continue

                score = abs(x - start_x) + abs(y - start_y)
                candidate = (score, x, y)
                if self.has_ground_below(sprite):
                    supported_candidates.append(candidate)
                else:
                    free_candidates.append(candidate)

        candidates = supported_candidates if prefer_floor and supported_candidates else free_candidates
        if candidates:
            _, x, y = min(candidates, key=lambda candidate: candidate[0])
            sprite.center_x = x
            sprite.center_y = y
            return

        sprite.center_x = min(max(start_x, search_margin), self.map_width - search_margin)
        sprite.center_y = min(max(start_y, search_margin), self.map_height - search_margin)

    def spawn_x_candidates(self, start_x, margin):
        step = max(16, self.tile_map.tile_width * self.tile_map.scaling / 2)
        max_offset = max(self.map_width, self.map_height)

        if self.entry_side == "right":
            ordered_offsets = self.spawn_offsets(step, max_offset)
            offsets = [0] + [-offset for offset in ordered_offsets] + ordered_offsets
        elif self.entry_side == "left":
            ordered_offsets = self.spawn_offsets(step, max_offset)
            offsets = [0] + ordered_offsets + [-offset for offset in ordered_offsets]
        else:
            offsets = self.bidirectional_spawn_offsets(step, max_offset)

        candidates = []
        for offset in offsets:
            x = min(max(start_x + offset, margin), self.map_width - margin)
            if x not in candidates:
                candidates.append(x)

        return candidates

    def spawn_y_candidates(self, start_y, margin):
        step = max(8, self.tile_map.tile_height * self.tile_map.scaling / 4)
        max_offset = max(self.map_width, self.map_height)

        if self.entry_side == "top":
            ordered_offsets = self.spawn_offsets(step, max_offset)
            offsets = [0] + [-offset for offset in ordered_offsets] + ordered_offsets
        elif self.entry_side in ("bottom", "left", "right"):
            ordered_offsets = self.spawn_offsets(step, max_offset)
            offsets = [0] + ordered_offsets + [-offset for offset in ordered_offsets]
        else:
            offsets = self.bidirectional_spawn_offsets(step, max_offset)

        candidates = []
        for offset in offsets:
            y = min(max(start_y + offset, margin), self.map_height - margin)
            if y not in candidates:
                candidates.append(y)

        return candidates

    @staticmethod
    def spawn_offsets(step, max_offset):
        offset = step
        offsets = []
        while offset <= max_offset:
            offsets.append(offset)
            offset += step

        return offsets

    @staticmethod
    def bidirectional_spawn_offsets(step, max_offset):
        offsets = [0]
        for offset in GameView.spawn_offsets(step, max_offset):
            offsets.extend((offset, -offset))

        return offsets

    def has_ground_below(self, sprite):
        original_y = sprite.center_y
        sprite.center_y -= max(4, self.tile_map.tile_height * self.tile_map.scaling / 8)
        has_ground = arcade.check_for_collision_with_list(sprite, self.platform_sprites)
        sprite.center_y = original_y
        return has_ground

    def spawn_from_tiled(self):
        if not self.tile_map.object_lists:
            return None

        for layer_name in SPAWN_OBJECT_LAYER_NAMES:
            if layer_name not in self.tile_map.object_lists:
                continue

            fallback_spawn = None
            for marker in self.tile_map.object_lists[layer_name]:
                marker_side = self.spawn_marker_side(marker)
                spawn_position = self.spawn_marker_position(marker)
                if marker_side == self.entry_side:
                    return spawn_position
                if marker_side in ("default", "start") and fallback_spawn is None:
                    fallback_spawn = spawn_position

            if fallback_spawn:
                return fallback_spawn

        return None

    @staticmethod
    def spawn_marker_side(marker):
        properties = marker.properties or {}
        for value in (
            properties.get("entry_side"),
            properties.get("side"),
            properties.get("spawn"),
            getattr(marker, "name", None),
            getattr(marker, "type", None),
        ):
            if value:
                return str(value).strip().lower()

        return None

    def spawn_marker_position(self, marker):
        coordinates = self.tile_map.get_cartesian(
            marker.shape[0],
            marker.shape[1],
        )
        return (
            math.floor(coordinates[0] * TILE_SCALING * self.tile_map.tile_width),
            math.floor((coordinates[1] + 1) * TILE_SCALING * self.tile_map.tile_height),
        )

    def connected_room(self, side):
        return ROOM_CONNECTIONS.get(self.current_room, {}).get(side)

    def adjacent_grid_room(self, side):
        row, column = self.current_room

        if side == "left":
            return (row, column - 1)
        if side == "right":
            return (row, column + 1)
        if side == "top":
            return (row - 1, column)
        if side == "bottom":
            return (row + 1, column)

        return None

    def sequential_side_room(self, side):
        if side not in ("left", "right") or self.current_room not in LEVEL_ORDER:
            return None

        room_index = LEVEL_ORDER.index(self.current_room)
        if side == "left" and room_index > 0:
            return LEVEL_ORDER[room_index - 1]
        if side == "right" and room_index < len(LEVEL_ORDER) - 1:
            return LEVEL_ORDER[room_index + 1]

        return None

    def activate_safe_room_checkpoint(self):
        if self.current_room not in SAFE_ROOMS:
            return

        self.lives = MAX_LIVES
        save_game(
            self.current_room,
            self.entry_side,
            score=self.score,
            lives=self.lives,
            has_checkpoint=True,
            daedalus_dialogue_complete=self.daedalus_dialogue_complete,
            feather_count=self.feather_count,
            cleared_feather_rooms=self.cleared_feather_rooms,
            has_double_jump=self.has_double_jump,
            has_dash=self.has_dash,
            has_wall_jump=self.has_wall_jump,
        )
        self.update_hud()

    def handle_room_exits(self):
        if (
            self.left_pressed
            and self.player_sprite.left <= SIDE_EXIT_MARGIN
        ):
            return self.try_exit_room("left")

        if (
            self.right_pressed
            and self.player_sprite.right >= self.map_width - SIDE_EXIT_MARGIN
        ):
            return self.try_exit_room("right")

        if (
            self.player_sprite.change_y > 0
            and self.player_sprite.top >= self.map_height
        ):
            return self.try_exit_room("top")

        if (
            self.player_sprite.change_y < 0
            and self.player_sprite.top < -FALL_VOID_MARGIN
        ):
            return self.try_exit_room("bottom")

        return False

    def try_exit_room(self, side):
        target_room = self.connected_room(side)
        if target_room and target_room in LEVEL_GRID:
            self.change_room(target_room, OPPOSITE_SIDE[side])
            return True

        if side == "bottom":
            self.lose_life()
            return True

        return False

    def change_room(self, target_room, entry_side):
        next_level = self.level_from_room(target_room)
        same_track = self._music_zone(self.current_room) == self._music_zone(target_room)

        if same_track:
            inherited_music = self.music
            inherited_player = self.music_player
            self.music = None
            self.music_player = None
        else:
            if self.music_player:
                self.music_player.delete()
                self.music_player = None
            inherited_music = None
            inherited_player = None

        new_game = GameView(
            level=next_level,
            score=self.score,
            lives=self.lives,
            room_position=target_room,
            entry_side=entry_side,
            inherited_music=inherited_music,
            inherited_music_player=inherited_player,
            daedalus_dialogue_complete=self.daedalus_dialogue_complete,
            inherited_overworld_track_index=self.overworld_track_index,
            feather_count=self.feather_count,
            cleared_feather_rooms=self.cleared_feather_rooms,
            has_double_jump=self.has_double_jump,
            has_dash=self.has_dash,
            has_wall_jump=self.has_wall_jump,
        )
        self.window.show_view(new_game)

    def enter_safe_room(self, side):
        self.entry_side = side
        self.lives = MAX_LIVES
        save_game(
            self.current_room,
            self.entry_side,
            score=self.score,
            lives=self.lives,
            has_checkpoint=True,
            daedalus_dialogue_complete=self.daedalus_dialogue_complete,
            feather_count=self.feather_count,
            cleared_feather_rooms=self.cleared_feather_rooms,
            has_double_jump=self.has_double_jump,
            has_dash=self.has_dash,
            has_wall_jump=self.has_wall_jump,
        )
        self.play_sfx(self.collect_coin_sound)
        self.place_player_at_entry()
        self.update_hud()

    def lose_life(self):
        self.lives -= 1
        self.feather_count = max(0, self.feather_count - 2)
        self.apply_feather_unlocks()
        self.update_hud()
        if self.lives != 0:
            arcade.play_sound(
            self.gameover_sound, 
            volume=SETTINGS.sfx_volume
        )


        elif self.lives <= 0:
            if self.gameover_voice:
                arcade.play_sound(
                    self.gameover_voice,
                    volume=SETTINGS.voice_volume * 0.5
                )
            if self.music_player:
                self.music_player.delete()
                self.music_player = None
            from views.transitions import FadeToView
            score = self.score
            self.window.show_view(
                FadeToView(self, lambda: GameOverView(score=score), duration=0.65)
            )
            return

        self.place_player_at_entry()
        self.player_sprite.is_dashing = False
        self.player_sprite.dash_timer = 0
        self.player_sprite.wall_sliding = False
        self.player_sprite.wall_jump_lock_timer = 0
        self.player_sprite.wall_jump_active = False
        self.update_hud()

    def update_hud(self):
        pass

    def load_feather_sprites(self):
        self.feather_sprites_normal = arcade.SpriteList()
        self.feather_sprites_golden = arcade.SpriteList()
        self.feather_sprites_blue = arcade.SpriteList()
        self._blue_trail_sprites = arcade.SpriteList()

        tex_n = arcade.load_texture(str(FEATHER_NORMAL_PATH))
        tex_g = arcade.load_texture(str(FEATHER_GOLDEN_PATH))
        tex_b = arcade.load_texture(str(FEATHER_BLUE_PATH))
        self._feather_hud_texture = tex_n
        self._tex_blue = tex_b
        self._tex_golden = tex_g

        # Cache de TODAS las capas sólidas del mapa (para _is_open_air)
        self._solid_sprite_lists = []
        for name, slist in self.scene._name_mapping.items():
            if name not in _NONSOLD_LAYERS and len(slist) > 0:
                self._solid_sprite_lists.append(slist)

        # No colocar plumas en salas ya recolectadas
        if self.current_room in self.cleared_feather_rooms:
            return

        if "Feathers" in self.tile_map.object_lists:
            for obj in self.tile_map.object_lists["Feathers"]:
                props = obj.properties or {}
                ftype = props.get("feather_type", "normal")
                cx, cy = self.tile_map.get_cartesian(obj.shape[0], obj.shape[1])
                if ftype == "golden":
                    s = arcade.Sprite(scale=0.9)
                    s.texture = tex_g
                    s.center_x, s.center_y = cx, cy
                    self.feather_sprites_golden.append(s)
                elif ftype == "blue":
                    s = arcade.Sprite(scale=0.9)
                    s.texture = tex_b
                    s.center_x, s.center_y = cx, cy
                    self.feather_sprites_blue.append(s)
                else:
                    s = arcade.Sprite(scale=0.9)
                    s.texture = tex_n
                    s.center_x, s.center_y = cx, cy
                    self.feather_sprites_normal.append(s)
        else:
            self._auto_place_feathers(tex_n, tex_g, tex_b)

    def _is_open_air(self, x, y, radius=56):
        lists = self._solid_sprite_lists if self._solid_sprite_lists else [self.platform_sprites]
        for slist in lists:
            for sprite in slist:
                if abs(sprite.center_x - x) < radius and abs(sprite.center_y - y) < radius:
                    return False
        return True

    def _find_open_air_positions(self, rng, count, min_y_frac=0.0, max_y_frac=1.0):
        positions = []
        tile = int(32 * TILE_SCALING)
        w = max(int(self.map_width) - tile, tile + 1)
        full_h = int(self.map_height)
        y_lo = max(tile, int(full_h * min_y_frac))
        y_hi = max(y_lo + 1, min(full_h - tile, int(full_h * max_y_frac)))
        for _ in range(count * 40):
            x = rng.randint(tile, w)
            y = rng.randint(y_lo, y_hi)
            if self._is_open_air(x, y):
                positions.append((x, y))
            if len(positions) >= count:
                break
        return positions

    def _auto_place_feathers(self, tex_n, tex_g, tex_b):
        rng = random.Random(hash(self.current_room))
        show_golden = rng.random() < FEATHER_GOLDEN_PROB

        # Normales: mitad baja-media del mapa (alcanzables con salto básico)
        normal_positions = self._find_open_air_positions(
            rng, FEATHER_NORMAL_COUNT + 3, min_y_frac=0.15, max_y_frac=0.60
        )
        normal_positions = normal_positions[:FEATHER_NORMAL_COUNT]

        # Dorada: zona alta (requiere doble salto o dash)
        golden_pos = None
        if show_golden:
            golden_candidates = self._find_open_air_positions(
                rng, 5, min_y_frac=0.60, max_y_frac=0.95
            )
            if golden_candidates:
                golden_pos = rng.choice(golden_candidates)

        # Azul trigger: zona media del mapa, cerca del centro horizontal
        blue_candidates = self._find_open_air_positions(
            rng, 8, min_y_frac=0.25, max_y_frac=0.70
        )
        mid_x = self.map_width / 2
        blue_pos = min(blue_candidates, key=lambda p: abs(p[0] - mid_x)) if blue_candidates else None

        for x, y in normal_positions:
            s = arcade.Sprite(scale=0.9)
            s.texture = tex_n
            s.center_x, s.center_y = x, y
            self.feather_sprites_normal.append(s)

        if golden_pos:
            s = arcade.Sprite(scale=0.9)
            s.texture = tex_g
            s.center_x, s.center_y = golden_pos
            self.feather_sprites_golden.append(s)

        if blue_pos:
            s = arcade.Sprite(scale=0.9)
            s.texture = tex_b
            s.center_x, s.center_y = blue_pos
            self.feather_sprites_blue.append(s)

    def _spawn_blue_trail(self, trigger_x, trigger_y):
        count = FEATHER_BLUE_TRAIL_COUNT
        step = 155   # distancia entre plumas consecutivas
        margin = 55
        rng = random.Random(hash(self.current_room) ^ 0xBEEF)

        # Zigzag simétrico: derecha, izquierda, derecha más lejos, ...
        # Máximo spread ≈ step * ceil(count/2) ≈ 620px del trigger
        offsets = []
        for i in range(count):
            half = (i // 2) + 1
            direction = 1 if i % 2 == 0 else -1
            offsets.append(direction * step * half)

        for offset in offsets:
            x = trigger_x + offset
            x = max(margin, min(x, self.map_width - margin))
            base_y = trigger_y + rng.randint(-60, 60)

            placed = False
            for dy in (0, 60, -60, 120, -120, 180, -180, 240, -240):
                cy = max(60, min(base_y + dy, self.map_height - 40))
                if self._is_open_air(x, cy):
                    base_y = cy
                    placed = True
                    break
            if not placed:
                for dx in (50, -50, 100, -100):
                    cx = max(margin, min(x + dx, self.map_width - margin))
                    for dy in (0, 60, -60, 120, -120):
                        cy = max(60, min(base_y + dy, self.map_height - 40))
                        if self._is_open_air(cx, cy):
                            x, base_y = cx, cy
                            placed = True
                            break
                    if placed:
                        break

            s = arcade.Sprite(scale=0.9)
            s.texture = self._tex_blue
            s.center_x = x
            s.center_y = base_y
            self._blue_trail_sprites.append(s)
        self.blue_trail_total = len(self._blue_trail_sprites)

    def _setup_shop(self):
        self.shop_sprite = None
        self.shop_data = None
        if self.current_room not in ABILITY_SHOPS:
            return
        shop = ABILITY_SHOPS[self.current_room]
        # Si la habilidad ya está comprada, no mostrar tienda
        if shop["type"] == "double_jump" and self.has_double_jump:
            return
        if shop["type"] == "dash" and self.has_dash:
            return
        if shop["type"] == "wall_jump" and self.has_wall_jump:
            return
        # Colocar marcador en aire libre, preferiblemente cerca del centro horizontal
        if not self._tex_golden:
            return
        rng = random.Random(hash(self.current_room) ^ 0xA17A4)
        candidates = self._find_open_air_positions(rng, 20, min_y_frac=0.15, max_y_frac=0.75)
        if not candidates:
            return
        mid_x = self.map_width / 2
        cx, cy = min(candidates, key=lambda p: abs(p[0] - mid_x))
        s = arcade.Sprite(scale=1.5)
        s.texture = self._tex_golden
        s.center_x, s.center_y = cx, cy
        self.shop_sprite = s
        self.shop_data = shop

    def _can_use_shop(self):
        if not self.shop_sprite or not self.shop_data or not self.player_sprite:
            return False
        dist = math.hypot(
            self.player_sprite.center_x - self.shop_sprite.center_x,
            self.player_sprite.center_y - self.shop_sprite.center_y,
        )
        return dist <= SHOP_INTERACT_DISTANCE

    def _use_shop(self):
        if not self.shop_data:
            return
        shop = self.shop_data
        cost = shop["cost"]
        stype = shop["type"]
        if stype == "life" and self.lives >= MAX_LIVES:
            return
        if self.feather_count < cost:
            return
        self.feather_count -= cost
        if stype == "life":
            self.lives = min(self.lives + 1, MAX_LIVES)
        elif stype == "double_jump":
            self.has_double_jump = True
            self.shop_sprite = None
            self.shop_data = None
        elif stype == "dash":
            self.has_dash = True
            self.shop_sprite = None
            self.shop_data = None
        elif stype == "wall_jump":
            self.has_wall_jump = True
            self.shop_sprite = None
            self.shop_data = None
        self.apply_feather_unlocks()
        self.update_hud()
        self.play_sfx(self.collect_coin_sound)

    def apply_feather_unlocks(self):
        if self.player_sprite is None:
            return
        self.player_sprite.has_double_jump = self.has_double_jump
        self.player_sprite.double_jump_available = self.has_double_jump
        self.player_sprite.has_dash = self.has_dash
        self.player_sprite.dash_available = self.has_dash
        self.player_sprite.has_wall_jump = self.has_wall_jump

    def add_feathers(self, amount):
        self.feather_count += amount
        self.cleared_feather_rooms.add(self.current_room)
        self.apply_feather_unlocks()
        self.play_sfx(self.collect_coin_sound)
        self.update_hud()

    def start_music(self):
        if self.music_player:
            self.music_player.delete()
        zone = self._music_zone(self.current_room)
        if zone == "overworld":
            self.overworld_track_index = 0
            self._play_overworld_track()
        elif zone == "underworld1":
            self.music = arcade.load_sound(str(UNDERWORLD_1_MUSIC), streaming=True)
            self.music_player = arcade.play_sound(
                self.music, volume=SETTINGS.music_volume, loop=True
            )
        elif zone == "underworld2":
            self.music = arcade.load_sound(str(UNDERWORLD_2_MUSIC), streaming=True)
            self.music_player = arcade.play_sound(
                self.music, volume=SETTINGS.music_volume, loop=True
            )
        else:
            music_path = LEVEL_MUSIC[self.level - 1]
            self.music = arcade.load_sound(str(music_path), streaming=True)
            self.music_player = arcade.play_sound(
                self.music, volume=SETTINGS.music_volume, loop=True
            )

    @staticmethod
    def _music_zone(room):
        if room in OVERWORLD_ROOMS:
            return "overworld"
        if room in UNDERWORLD_1_ROOMS:
            return "underworld1"
        if room in UNDERWORLD_2_ROOMS:
            return "underworld2"
        return "earth"

    def _play_overworld_track(self):
        path = OVERWORLD_MUSIC[self.overworld_track_index % len(OVERWORLD_MUSIC)]
        self.music = arcade.load_sound(str(path), streaming=True)
        self.music_player = arcade.play_sound(
            self.music, volume=SETTINGS.music_volume, loop=False
        )

    def on_show_view(self):
        self.window.ctx.viewport = (
            0,
            0,
            self.window.width,
            self.window.height
        )

        if self.camera:
            self.camera.match_window()

        if self.gui_camera:
            self.gui_camera.match_window()

        if not self.initialized:
            self.setup()
            self.initialized = True
        elif self.music_player:
            self.music_player.volume = SETTINGS.music_volume

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate our camera before drawing
        self.camera.use()

        # Draw our Scene
        self.scene.draw()
        self.feather_sprites_normal.draw()
        self.feather_sprites_golden.draw()
        self.feather_sprites_blue.draw()
        self._blue_trail_sprites.draw()
        if self.shop_sprite:
            arcade.draw_circle_filled(
                self.shop_sprite.center_x, self.shop_sprite.center_y + 8,
                36, (212, 165, 78, 55),
            )
            arcade.draw_sprite(self.shop_sprite)

        # Activate our GUI camera
        self.gui_camera.use()

        self._draw_hud()
        self._draw_interaction_prompt()
        self._draw_dialogue_box()
        self.draw_crt_filter()

    def _draw_hud(self):
        h = self.window.height
        pad = 14
        font = "Garamond"

        filled = "♥ " * self.lives
        empty  = "♡ " * (MAX_LIVES - self.lives)
        arcade.draw_text(
            (filled + empty).strip(),
            pad, h - 20,
            (196, 72, 72),
            17,
            anchor_x="left",
            anchor_y="center",
            font_name=font,
        )

        if self._feather_hud_texture:
            icon = 18
            arcade.draw_texture_rect(
                self._feather_hud_texture,
                arcade.LBWH(pad, h - 50 - icon // 2, icon, icon),
            )
            arcade.draw_text(
                str(self.feather_count),
                pad + icon + 4, h - 50,
                (180, 210, 245),
                13,
                anchor_x="left",
                anchor_y="center",
                font_name=font,
            )

        if self.blue_timer_active:
            color = (100, 180, 255) if self.blue_timer_remaining > 5 else (255, 80, 80)
            cx = self.window.width / 2
            arcade.draw_text(
                f"{self.blue_timer_remaining:.1f}s",
                cx, h - 20,
                color,
                22,
                anchor_x="center",
                anchor_y="center",
                font_name=font,
                bold=True,
            )
            collected = self.blue_trail_total - len(self._blue_trail_sprites)
            arcade.draw_text(
                f"{collected} / {self.blue_trail_total}",
                cx, h - 46,
                (180, 210, 245),
                15,
                anchor_x="center",
                anchor_y="center",
                font_name=font,
            )

    def _draw_interaction_prompt(self):
        if self.dialogue_active:
            return
        cx = self.window.width / 2
        font = "Garamond"

        if self.can_talk_to_daedalus():
            text = "[E]  Hablar con Dédalo"
            color = (212, 165, 78)
        elif self._can_use_shop():
            shop = self.shop_data
            cost = shop["cost"]
            stype = shop["type"]
            if stype == "life" and self.lives >= MAX_LIVES:
                text = "Vida máxima — no puedes comprar más"
                color = (150, 150, 150)
            elif self.feather_count < cost:
                text = f"[E]  {shop['label']}  —  {cost} plumas  (tienes {self.feather_count})"
                color = (200, 80, 80)
            else:
                text = f"[E]  {shop['label']}  —  {cost} plumas"
                color = (212, 165, 78)
        else:
            return

        prompt_w = max(260, len(text) * 8)
        prompt_h = 30
        arcade.draw_rect_filled(
            arcade.LBWH(cx - prompt_w / 2, 66, prompt_w, prompt_h),
            (8, 10, 17, 190),
        )
        arcade.draw_rect_outline(
            arcade.LBWH(cx - prompt_w / 2, 66, prompt_w, prompt_h),
            (*color[:3], 180), 1,
        )
        arcade.draw_text(
            text, cx, 81, color, 14,
            anchor_x="center", anchor_y="center", font_name=font,
        )

    def _draw_dialogue_box(self):
        line = self.current_dialogue_line()
        if not line:
            return

        box_margin = 42
        box_height = 154
        box_y = 34
        box_width = self.window.width - box_margin * 2
        box = arcade.LBWH(box_margin, box_y, box_width, box_height)
        arcade.draw_rect_filled(box, (8, 10, 17, 224))
        arcade.draw_rect_outline(box, (212, 165, 78, 210), 2)

        text_x = box_margin + 28
        text_y = box_y + box_height - 34
        speaker = line["speaker"]
        if speaker:
            arcade.draw_text(
                speaker,
                text_x,
                text_y,
                (212, 165, 78),
                18,
                anchor_x="left",
                anchor_y="center",
                font_name="Garamond",
                bold=True,
            )
            text_y -= 34

        for wrapped_line in textwrap.wrap(line["text"], width=86):
            arcade.draw_text(
                wrapped_line,
                text_x,
                text_y,
                (238, 230, 206),
                17,
                anchor_x="left",
                anchor_y="center",
                font_name="Garamond",
            )
            text_y -= 24

        arcade.draw_text(
            "Enter / Espacio",
            box_margin + box_width - 28,
            box_y + 18,
            (176, 166, 142),
            13,
            anchor_x="right",
            anchor_y="center",
            font_name="Garamond",
        )

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        if not self.initialized or not self.player_sprite or not self.physics_engine:
            return

        if self.dialogue_active:
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.scene.update_animation(delta_time, ["Player", "NPCs"])
            if self.daedalus_npc and self.daedalus_textures:
                self.daedalus_anim_timer += delta_time
                n = len(self.daedalus_textures)
                self.daedalus_npc.texture = self.daedalus_textures[int(self.daedalus_anim_timer * 12.5) % n]
            if self.zeus_npc and self.zeus_textures:
                self.zeus_anim_timer += delta_time
                n = len(self.zeus_textures)
                self.zeus_npc.texture = self.zeus_textures[int(self.zeus_anim_timer * 12.5) % n]
            return

        # --- WALL JUMP LOCK TIMER ---
        was_wall_jump_locked = self.player_sprite.wall_jump_lock_timer > 0
        if self.player_sprite.wall_jump_lock_timer > 0:
            self.player_sprite.wall_jump_lock_timer = max(
                0,
                self.player_sprite.wall_jump_lock_timer - delta_time
            )

        if (
            was_wall_jump_locked
            and self.player_sprite.wall_jump_lock_timer <= 0
        ):
            self.player_sprite.wall_jump_active = False
            self.process_keychange()

        was_jump_locked = self.player_sprite.jump_lock_timer > 0
        if self.player_sprite.jump_lock_timer > 0:
            self.player_sprite.jump_lock_timer = max(
                0,
                self.player_sprite.jump_lock_timer - delta_time
            )

        if (
            was_jump_locked
            and self.player_sprite.jump_lock_timer <= 0
            and self.jump_queued
        ):
            self.process_keychange()

        if self.player_sprite.dash_input_lock_timer > 0:
            self.player_sprite.dash_input_lock_timer = max(
                0,
                self.player_sprite.dash_input_lock_timer - delta_time
            )

        # --- WALL SLIDE ---
        self.player_sprite.wall_sliding = False

        if self.player_sprite.has_wall_jump:

            self.touching_left_wall = False
            self.touching_right_wall = False

            # mover temporalmente para comprobar pared izquierda
            self.player_sprite.center_x -= 2
            if arcade.check_for_collision_with_list(
                self.player_sprite,
                self.platform_sprites
            ):
                self.touching_left_wall = True

            # comprobar pared derecha
            self.player_sprite.center_x += 4
            if arcade.check_for_collision_with_list(
                self.player_sprite,
                self.platform_sprites
            ):
                self.touching_right_wall = True

            # restaurar posición original
            self.player_sprite.center_x -= 2

            touching_wall = self.touching_left_wall or self.touching_right_wall

            # Guardar última pared tocada
            if self.touching_left_wall:
                self.last_wall_touched = -1
            elif self.touching_right_wall:
                self.last_wall_touched = 1

            on_ground = self.physics_engine.can_jump()

            moving_down = self.player_sprite.change_y <= 0

            pressing_wall = (
                (self.left_pressed and self.touching_left_wall)
                or
                (self.right_pressed and self.touching_right_wall)
            )

            if (
                touching_wall
                and not on_ground
                and moving_down
                and pressing_wall
                and self.player_sprite.wall_jump_lock_timer <= 0
            ):

                self.player_sprite.wall_sliding = True
                self.wall_jump_wall_direction = self.current_wall_direction()

                # Limitar velocidad de caída
                if self.player_sprite.change_y < WALL_SLIDE_SPEED:
                    self.player_sprite.change_y = WALL_SLIDE_SPEED

       # --- DASH UPDATE ---
        if self.player_sprite.is_dashing:

            # Mantener velocidad constante
            if self.player_sprite.facing_direction == RIGHT_FACING:
                self.player_sprite.change_x = DASH_SPEED
            else:
                self.player_sprite.change_x = -DASH_SPEED

            # Sin gravedad
            self.player_sprite.change_y = 0

            # Contador dash
            self.player_sprite.dash_timer -= delta_time

            # Fin dash
            if self.player_sprite.dash_timer <= 0:

                self.player_sprite.is_dashing = False

                # Frenar velocidad del dash
                self.player_sprite.change_x *= 0.3

                # Recalcular movimiento normal
                self.process_keychange()

        # --- DASH COOLDOWN ---
        if self.player_sprite.dash_cooldown_timer > 0:
            self.player_sprite.dash_cooldown_timer -= delta_time
        else:
            self.player_sprite.dash_available = True

        if self.physics_engine.can_jump():
            self.player_sprite.coyote_timer = 0.12
            # Reset doble salto al tocar suelo
            self.player_sprite.double_jump_available = False
            self.player_sprite.double_jump_used = False
            self.player_sprite.dash_available = True
            # Reiniciar última pared al tocar suelo
            self.player_sprite.last_wall_jumped = 0

        else:
            self.player_sprite.coyote_timer = max(
                0, self.player_sprite.coyote_timer - delta_time
            )

            if (
                self.player_sprite.has_double_jump
                and not self.player_sprite.double_jump_used
                and not self.player_sprite.double_jump_available
                and self.player_sprite.change_y <= 0
            ):
                self.player_sprite.double_jump_available = True
        # --- Better Jump ---
        if not self.player_sprite.is_dashing:

            # Caída más rápida
            if self.player_sprite.change_y < 0:
                self.player_sprite.change_y -= GRAVITY * 0.5

            # Salto variable
            elif self.player_sprite.change_y > 0:
                if not self.player_sprite.jump_pressed:
                    self.player_sprite.change_y -= GRAVITY * 1.5

        # Update our characters animation state
        if self.physics_engine.is_on_ladder():
            self.player_sprite.climbing = True
        else:
            self.player_sprite.climbing = False

        # Move the player using our physics engine
        self.physics_engine.update()
        self.cancel_wall_jump_on_collision()
        if self.handle_room_exits():
            return

        self.keep_player_inside_map()

        if arcade.check_for_collision_with_list(
            self.player_sprite,
            self.reset_sprites
        ):
            self.lose_life()
            return
        
        # Actually trigger animation updates. We've added the Background and Coins layer
        # here as well. Our Tiled map has some animated tiles built-in, check out the flags
        # and torches on the map.
        self.scene.update_animation(
            delta_time,
            [
                "Coins",
                "Player",
                "Enemies"
            ]
        )

        if self.daedalus_npc and self.daedalus_textures:
            self.daedalus_anim_timer += delta_time
            n = len(self.daedalus_textures)
            self.daedalus_npc.texture = self.daedalus_textures[int(self.daedalus_anim_timer * 12.5) % n]

        if self.zeus_npc and self.zeus_textures:
            self.zeus_anim_timer += delta_time
            n = len(self.zeus_textures)
            self.zeus_npc.texture = self.zeus_textures[int(self.zeus_anim_timer * 12.5) % n]

        if (
            self.current_room in OVERWORLD_ROOMS
            and self.music_player is not None
            and not self.music_player.playing
        ):
            self.overworld_track_index += 1
            self._play_overworld_track()

        self.scene.update(delta_time, ["Enemies"])

        # Keep enemies walking within their boundaries configured in Tiled
        for enemy in self.scene["Enemies"]:
            if enemy.right > enemy.boundary_right and enemy.change_x > 0:
                enemy.change_x *= -1
            elif enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1

        # See if we hit any coins
        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.coin_sprites,
                self.enemy_sprites
            ]
        )

        for collision in player_collision_list:
            if self.enemy_sprites in collision.sprite_lists:
                self.lose_life()
                return
            else:
                # Our collision is a coin, remove it
                collision.remove_from_sprite_lists()
                self.play_sfx(self.collect_coin_sound)
                self.score += 75
                self.update_hud()

        # Feathers
        for f in arcade.check_for_collision_with_list(self.player_sprite, self.feather_sprites_normal):
            f.remove_from_sprite_lists()
            self.add_feathers(1)

        for f in arcade.check_for_collision_with_list(self.player_sprite, self.feather_sprites_golden):
            f.remove_from_sprite_lists()
            self.add_feathers(FEATHER_GOLDEN_VALUE)

        # Trigger azul — al tocarlo desaparece para siempre y spawnea la estela
        if not self.blue_timer_active:
            for f in arcade.check_for_collision_with_list(self.player_sprite, self.feather_sprites_blue):
                tx, ty = f.center_x, f.center_y
                f.remove_from_sprite_lists()
                self._spawn_blue_trail(tx, ty)
                self.blue_timer_active = True
                self.blue_timer_remaining = FEATHER_BLUE_TIMER
                self._tick_timer = 0.0
                if self.music_player:
                    self.music_player.volume = SETTINGS.music_volume * BLUE_MUSIC_DUCK
                break

        # Estela azul — recoger durante el reto
        if self.blue_timer_active:
            for f in arcade.check_for_collision_with_list(self.player_sprite, self._blue_trail_sprites):
                f.remove_from_sprite_lists()

            if self.blue_trail_total > 0 and len(self._blue_trail_sprites) == 0:
                self.blue_timer_active = False
                self.blue_trail_total = 0
                if self.music_player:
                    self.music_player.volume = SETTINGS.music_volume
                self.add_feathers(FEATHER_BLUE_REWARD)

            self.blue_timer_remaining -= delta_time
            if self.blue_timer_remaining <= 0:
                self.blue_timer_active = False
                self.blue_trail_total = 0
                self._blue_trail_sprites.clear()
                if self.music_player:
                    self.music_player.volume = SETTINGS.music_volume
                # Penalización por fallo
                self.feather_count = max(0, self.feather_count - FEATHER_BLUE_PENALTY)
                self.apply_feather_unlocks()
                self.update_hud()
                self.play_sfx(self.hit_sound)

            # Tick sound cada segundo
            self._tick_timer -= delta_time
            if self._tick_timer <= 0:
                self._tick_timer = 1.0
                self.play_sfx(self._tick_sound)

        self.update_camera()

    def perform_wall_jump(self):
        wall_direction = (
            self.wall_jump_wall_direction
            or self.current_wall_direction()
        )

        if wall_direction == 0:
            self.jump_queued = False
            return
        # Salto flojo (misma pared)
        if self.player_sprite.last_wall_jumped == wall_direction:
            jump_force_y = WALL_JUMP_REPEAT_FORCE_Y
            jump_force_x = WALL_JUMP_REPEAT_FORCE_X

        #Salto fuerte
        else:
            jump_force_y = WALL_JUMP_FORCE_Y
            jump_force_x = WALL_JUMP_FORCE_X

        # Aplicar fuerzas
        self.player_sprite.change_y = jump_force_y
        self.player_sprite.change_x = -wall_direction * jump_force_x

        # Guardar última pared usada
        self.player_sprite.last_wall_jumped = wall_direction

        self.player_sprite.wall_sliding = False
        self.player_sprite.wall_jump_lock_timer = WALL_JUMP_LOCK_TIME
        self.player_sprite.wall_jump_active = True
        self.player_sprite.jump_lock_timer = DOUBLE_JUMP_LOCK_TIME
        self.player_sprite.double_jump_available = False
        self.jump_queued = False

        arcade.play_sound(
            self.jump_sound,
            volume=SETTINGS.sfx_volume
        )

        self.maybe_play_movement_voice()

    def current_wall_direction(self):
        if self.touching_left_wall and not self.touching_right_wall:
            return -1
        if self.touching_right_wall and not self.touching_left_wall:
            return 1
        if self.left_pressed and self.touching_left_wall:
            return -1
        if self.right_pressed and self.touching_right_wall:
            return 1

        return 0

    def process_keychange(self):
        # First handle the case where we have moved up. This needs to be handled
        # differently to move the player upwards if they are on a ladder, or
        # perform a jump if they are not on a ladder. This code might look
        # different if we had a separate button for jumping, we would only need
        # to handle moving upwards if we were on a ladder for the up key then.
        # Here we also handle the case where we have moved down while on a ladder.
        # Coyote Jump is a mechanic that allows the user to have a more permissive jump
        # allowing them to jump even if theres no floor for a couple seconds

        
        if self.player_sprite.is_dashing:
            return
        
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.jump_queued
                and self.player_sprite.jump_lock_timer <= 0
                and (
                    self.physics_engine.can_jump(y_distance=10)
                    or self.player_sprite.coyote_timer > 0
                )
            ):
                
                # Salto normal
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.player_sprite.coyote_timer = 0
                self.player_sprite.jump_lock_timer = DOUBLE_JUMP_LOCK_TIME
                self.player_sprite.double_jump_available = False
                self.player_sprite.double_jump_used = False
                self.jump_queued = False

                arcade.play_sound(
                    self.jump_sound,
                    volume=SETTINGS.sfx_volume
                )
                self.maybe_play_movement_voice()

            elif self.jump_queued and self.player_sprite.wall_sliding:
                self.perform_wall_jump()

            elif self.jump_queued and self.player_sprite.has_double_jump:
                if (
                    self.player_sprite.double_jump_available
                    and self.player_sprite.jump_lock_timer <= 0
                ):
                    # Doble salto
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
                    self.jump_queued = False

                    # Gastar doble salto
                    self.player_sprite.double_jump_available = False
                    self.player_sprite.double_jump_used = True

                    arcade.play_sound(
                        self.jump_sound,
                        volume=SETTINGS.sfx_volume
                    )
                    self.maybe_play_movement_voice()
                elif self.player_sprite.jump_lock_timer > 0:
                    pass
                else:
                    self.jump_queued = False
            elif self.jump_queued and self.player_sprite.wall_sliding:

                # Impulso vertical
                self.player_sprite.change_y = WALL_JUMP_FORCE_Y

                # Impulso horizontal contrario
                if self.player_sprite.facing_direction == RIGHT_FACING:
                    self.player_sprite.change_x = -WALL_JUMP_FORCE_X
                else:
                    self.player_sprite.change_x = WALL_JUMP_FORCE_X

                arcade.play_sound(
                    self.jump_sound,
                    volume=SETTINGS.sfx_volume
                )
                self.maybe_play_movement_voice()
                # Evitar volver a agarrarse instantáneamente
                self.player_sprite.wall_jump_lock_timer = WALL_JUMP_LOCK_TIME
                self.player_sprite.wall_jump_active = True
                self.player_sprite.jump_lock_timer = DOUBLE_JUMP_LOCK_TIME
                self.jump_queued = False

            elif self.jump_queued:
                self.jump_queued = False

        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Now we need a special handling of our vertical movement while we are 
        # on a ladder, but have no input specified. When we jump, the physics
        # engine takes care of resetting our vertical movement to zero once we've
        # hit the ground. However for ladders, we need to ensure that we set the
        # vertical movement back to zero if the user does not give input, otherwise
        # once a user starts climbing a ladder, they will move upwards automatically
        # until they reach the end of the ladder. You can try commenting out this
        # block to see what that effect looks like.
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Now we just handle our horizontal movement, very similar to how we
        # did before, but now just combined in our new function.
        # Durante wall jump lock no aceptar control horizontal
        if self.player_sprite.wall_jump_lock_timer > 0:
            return

        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0
        
        

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if self.dialogue_active:
            if key in (arcade.key.ENTER, arcade.key.SPACE):
                self.advance_dialogue()
            elif key == arcade.key.ESCAPE:
                self.dialogue_active = False
                self.stop_dialogue_voice()
            return

        if key == arcade.key.E:
            if self.can_talk_to_daedalus():
                self.start_daedalus_dialogue()
                return
            if self._can_use_shop():
                self._use_shop()
                return

        if key == SETTINGS.key_pause:
            from views.pause_view import PauseMenuView
            self.window.show_view(PauseMenuView(self))
            return

        if key == SETTINGS.key_restart:
            new_game = GameView(
                level=self.level,
                score=self.score,
                lives=self.lives,
                room_position=self.current_room,
                entry_side=self.entry_side,
                daedalus_dialogue_complete=self.daedalus_dialogue_complete,
            )
            self.window.show_view(new_game)
            return

        if key == SETTINGS.key_up:
            if not self.up_pressed:
                self.jump_queued = True
            self.up_pressed = True
            self.player_sprite.jump_pressed = True
        elif key == SETTINGS.key_down:
            self.down_pressed = True
        elif key == SETTINGS.key_left:
            self.left_pressed = True
        elif key == SETTINGS.key_right:
            self.right_pressed = True

        # --- DASH ---
        if key == SETTINGS.key_dash:

            if (
                self.player_sprite.has_dash
                and self.player_sprite.dash_available
                and self.player_sprite.dash_input_lock_timer <= 0
                and not self.player_sprite.is_dashing
            ):

                self.player_sprite.is_dashing = True
                self.player_sprite.dash_available = False
                self.player_sprite.dash_timer = DASH_DURATION
                self.player_sprite.dash_cooldown_timer = DASH_COOLDOWN
                self.player_sprite.dash_input_lock_timer = DASH_INPUT_LOCK_TIME

                # Dirección del dash
                if self.player_sprite.facing_direction == RIGHT_FACING:
                    self.player_sprite.change_x = DASH_SPEED
                else:
                    self.player_sprite.change_x = -DASH_SPEED

                # Quitar velocidad vertical
                self.player_sprite.change_y = 0
                self.maybe_play_movement_voice()

        self.process_keychange()

    def on_key_release(self, key, modifiers):

        if key == SETTINGS.key_left:
            self.left_pressed = False

        elif key == SETTINGS.key_right:
            self.right_pressed = False

        elif key == SETTINGS.key_up:
            self.up_pressed = False
            self.player_sprite.jump_pressed = False
            self.jump_queued = False

        elif key == SETTINGS.key_down:
            self.down_pressed = False

        self.process_keychange()

    def on_resize(self, width, height):

        super().on_resize(width, height)

        # Actualizar viewport OpenGL
        self.window.ctx.viewport = (0, 0, width, height)

        # Actualizar cámaras
        if self.camera:
            self.camera.match_window()

        if self.gui_camera:
            self.gui_camera.match_window()

    def update_music_volume(self):
        if self.music_player:
            self.music_player.volume = SETTINGS.music_volume

    def play_sfx(self, sound):
        arcade.play_sound(
            sound,
            volume=SETTINGS.sfx_volume
        )

    def draw_crt_filter(self):
        width = self.window.width
        height = self.window.height

        for y in range(0, height, 8):
            arcade.draw_rect_filled(
                arcade.LBWH(0, y, width, 2),
                (0, 0, 0, 50)
            )

        arcade.draw_rect_filled(
            arcade.LBWH(0, 0, width, height),
            (24, 12, 32, 45)
        )

    def cancel_wall_jump_on_collision(self):
        if not self.player_sprite.wall_jump_active:
            return

        if self.physics_engine.can_jump():
            self.player_sprite.wall_jump_active = False
            self.player_sprite.wall_jump_lock_timer = 0
            self.process_keychange()

    def is_touching_wall(self):
        self.player_sprite.center_x -= 2
        touching_left = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.platform_sprites
        )

        self.player_sprite.center_x += 4
        touching_right = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.platform_sprites
        )

        self.player_sprite.center_x -= 2

        return bool(touching_left or touching_right)

    def keep_player_inside_map(self):
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
            self.player_sprite.change_x = max(0, self.player_sprite.change_x)

        if self.player_sprite.right > self.map_width:
            self.player_sprite.right = self.map_width
            self.player_sprite.change_x = min(0, self.player_sprite.change_x)

        if self.player_sprite.top > self.map_height:
            self.player_sprite.top = self.map_height
            self.player_sprite.change_y = min(0, self.player_sprite.change_y)

    def update_camera(self):
        viewport_width = self.window.width
        viewport_height = self.window.height

        if self.map_width <= viewport_width:
            camera_x = self.map_width / 2
        else:
            camera_x = max(
                viewport_width / 2,
                min(
                    self.player_sprite.center_x,
                    self.map_width - viewport_width / 2
                )
            )

        if self.map_height <= viewport_height:
            camera_y = self.map_height / 2
        else:
            camera_y = max(
                viewport_height / 2,
                min(
                    self.player_sprite.center_y,
                    self.map_height - viewport_height / 2
                )
            )

        self.camera.position = (camera_x, camera_y)
    
    def next_level(self):

        next_level_number = self.level + 1

        # Si no hay más niveles
        if next_level_number > len(LEVELS):
            print("Juego completado")
            return

        if self.music_player:
            self.music_player.delete()
            self.music_player = None

        new_game = GameView(
            level=next_level_number,
            score=self.score,
            lives=self.lives,
            entry_side=DEFAULT_ENTRY_SIDE,
        )
        self.window.show_view(new_game)

_DEATH_PHRASES = [
    "Hasta los dioses caen.",
    "El Olimpo no se conquista en un día.",
    "Incluso Aquiles tuvo un talón.",
    "Hades ya te conoce. Vuelve diferente.",
    "La gloria no se rinde.",
    "Ni Zeus ganó sin perder antes.",
    "El inframundo puede esperar.",
    "Los héroes no mueren. Regresan.",
    "Hermes cayó. Hermes volverá.",
    "La muerte es solo un desvío.",
]

_EMBER_COLORS = [(255, 130, 50), (255, 210, 70), (210, 60, 50)]


class GameOverView(arcade.View):

    _STAR_COUNT  = 120
    _EMBER_COUNT = 22

    def __init__(self, score=0, game_view=None):
        super().__init__()
        self.score = score
        self.selected_index = 0
        self.font_name = "Garamond"
        self.cream = (238, 230, 206)
        self.muted  = (176, 166, 142)
        self.gold   = (212, 165, 78)
        self.phrase       = random.choice(_DEATH_PHRASES)
        self.phrase_alpha = 255
        self.phrase_timer = 0.0
        self.phrase_state = "showing"   # showing | fading_out | fading_in
        self._SHOW_TIME   = 7.0
        self._FADE_TIME   = 1.0
        self.options = [
            ("Reintentar",    self._retry),
            ("Menu principal", self._go_menu),
        ]
        self.button_hitboxes = []
        self.time   = 0.0
        self.stars  = []
        self.embers = []
        self.music        = arcade.load_sound("../assets/Music/OST/Menu_Caido.ogg", streaming=True)
        self.music_player = None

    # ------------------------------------------------------------------ #
    #  Particles                                                           #
    # ------------------------------------------------------------------ #

    def _init_particles(self, w, h):
        self.stars = [
            {
                'x':     random.uniform(0, w),
                'y':     random.uniform(0, h),
                'r':     random.choice([0.7, 0.7, 1.2, 1.2, 1.8]),
                'phase': random.uniform(0, math.tau),
                'speed': random.uniform(2.0, 6.0),
                'base':  random.randint(35, 155),
            }
            for _ in range(self._STAR_COUNT)
        ]
        self.embers = [self._spawn_ember(w, h, born=True)
                       for _ in range(self._EMBER_COUNT)]

    def _spawn_ember(self, w, h, born=False):
        return {
            'x':        random.uniform(w * 0.05, w * 0.95),
            'y':        random.uniform(0, h * 0.25) if born else -8,
            'vx':       random.uniform(-14, 14),
            'vy':       random.uniform(35, 100),
            'r':        random.uniform(1.4, 3.2),
            'color':    random.choice(_EMBER_COLORS),
            'life':     0.0,
            'max_life': random.uniform(2.5, 5.5),
        }

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        if not self.stars:
            self._init_particles(self.window.width, self.window.height)
        self.music_player = arcade.play_sound(self.music, volume=SETTINGS.music_volume * 0.75, loop=True)

    def on_update(self, delta_time):
        self.time += delta_time
        self.phrase_timer += delta_time

        if self.phrase_state == "showing":
            self.phrase_alpha = 255
            if self.phrase_timer >= self._SHOW_TIME:
                self.phrase_state = "fading_out"
                self.phrase_timer = 0.0
        elif self.phrase_state == "fading_out":
            self.phrase_alpha = int(255 * max(0, 1 - self.phrase_timer / self._FADE_TIME))
            if self.phrase_timer >= self._FADE_TIME:
                others = [p for p in _DEATH_PHRASES if p != self.phrase]
                self.phrase = random.choice(others)
                self.phrase_state = "fading_in"
                self.phrase_timer = 0.0
        elif self.phrase_state == "fading_in":
            self.phrase_alpha = int(255 * min(1, self.phrase_timer / self._FADE_TIME))
            if self.phrase_timer >= self._FADE_TIME:
                self.phrase_state = "showing"
                self.phrase_timer = 0.0

        w, h = self.window.width, self.window.height
        for e in self.embers:
            e['life'] += delta_time
            e['x']   += e['vx'] * delta_time
            e['y']   += e['vy'] * delta_time
            if e['life'] >= e['max_life'] or e['y'] > h + 16:
                e.update(self._spawn_ember(w, h))

    # ------------------------------------------------------------------ #
    #  Drawing                                                             #
    # ------------------------------------------------------------------ #

    def on_draw(self):
        self.clear()
        w = self.window.width
        h = self.window.height
        self.button_hitboxes = []

        arcade.draw_rect_filled(arcade.LBWH(0, 0, w, h), (4, 4, 10))

        # Estrellas que titilan
        for s in self.stars:
            t     = 0.5 + 0.5 * math.sin(self.time * s['speed'] + s['phase'])
            alpha = int(s['base'] + (230 - s['base']) * t)
            arcade.draw_circle_filled(s['x'], s['y'], s['r'], (215, 205, 255, alpha))

        # Brasas que ascienden
        for e in self.embers:
            t     = e['life'] / e['max_life']
            alpha = int(220 * (1 - t ** 0.55))
            if alpha > 0:
                arcade.draw_circle_filled(e['x'], e['y'], e['r'], (*e['color'], alpha))

        cx      = w / 2
        title_y = h * 0.66

        # Halo dorado detrás del título
        arcade.draw_text(
            "CAÍDO", cx, title_y,
            (212, 165, 78, 32), 44,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
        )
        # Título
        arcade.draw_text(
            "CAÍDO", cx, title_y,
            self.cream, 36,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
        )
        arcade.draw_line(
            cx - 64, title_y - 26,
            cx + 64, title_y - 26,
            (212, 165, 78, 60), 1,
        )

        # Frase motivadora
        arcade.draw_text(
            self.phrase,
            cx, title_y - 52,
            (176, 166, 142, self.phrase_alpha), 16,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
            italic=True,
        )

        # Puntuación
        arcade.draw_text(
            f"✦  {self.score}",
            cx, h * 0.49,
            self.gold, 17,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
        )

        # Botones
        start_y = h * 0.39
        for i, (label, _) in enumerate(self.options):
            self._draw_button(i, label, cx, start_y - i * 52, i == self.selected_index)

        arcade.draw_text(
            "W S  ·  Enter  ·  Esc",
            cx, 40,
            (176, 166, 142, 70), 13,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
        )

    def _draw_button(self, index, label, x, y, selected):
        bw, bh = 270, 42
        left, right   = x - bw / 2, x + bw / 2
        bottom, top   = y - bh / 2, y + bh / 2
        self.button_hitboxes.append((index, left, right, bottom, top))

        arcade.draw_text(
            label, x, y,
            (255, 255, 255) if selected else (190, 182, 162),
            28 if selected else 22,
            anchor_x="center", anchor_y="center",
            font_name=self.font_name,
            bold=selected,
        )

    # ------------------------------------------------------------------ #
    #  Input                                                               #
    # ------------------------------------------------------------------ #

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            self.selected_index = (self.selected_index - 1) % len(self.options)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected_index = (self.selected_index + 1) % len(self.options)
        elif key == arcade.key.ESCAPE:
            self.selected_index = 1
            self._activate()
        elif key in (arcade.key.ENTER, arcade.key.SPACE):
            self._activate()

    def on_mouse_motion(self, x, y, dx, dy):
        for i, left, right, bottom, top in self.button_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = i
                return

    def on_mouse_press(self, x, y, button, modifiers):
        for i, left, right, bottom, top in self.button_hitboxes:
            if left <= x <= right and bottom <= y <= top:
                self.selected_index = i
                self._activate()
                return

    def _activate(self):
        _, action = self.options[self.selected_index]
        action()

    def _stop_music(self):
        if self.music_player:
            self.music_player.delete()
            self.music_player = None

    def _retry(self):
        self._stop_music()
        from views.transitions import FadeToView
        self.window.show_view(FadeToView(self, GameView, duration=0.6))

    def _go_menu(self):
        self._stop_music()
        from views.menu_view import MainMenu
        from views.transitions import FadeToView
        self.window.show_view(FadeToView(self, MainMenu, duration=0.7))

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.window.ctx.viewport = (0, 0, width, height)
        self._init_particles(width, height)

