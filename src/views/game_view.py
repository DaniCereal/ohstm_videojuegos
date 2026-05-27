import arcade
import math

from data.settings import SETTINGS

from constants import *

from data.settings import SETTINGS
import cv2
from models.player import PlayerCharacter

from models.enemy import (
    RobotEnemy,
    ZombieEnemy
)

LEVELS = [
    "../assets/Mapas/TierraArriba1.tmx",
    "../assets/Mapas/TierraArriba2.tmx",
    "../assets/Mapas/TierraArriba3.tmx",
    "../assets/Mapas/SavePointTierra.tmx"
]

class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self, level=1, score=0):

        # Call the parent class and set up the window
        super().__init__()

        self.level = level
        self.initialized = False
        self.score = score
        # Track the current state of our input
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False

        # Variable to hold our texture for our player
        self.player_texture = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Variable to hold our Tiled Map
        self.tile_map = None

        # Replacing all of our SpriteLists with a Scene variable
        self.scene = None

        # A variable to store our camera object
        self.camera = None

        # A variable to store our gui camera object
        self.gui_camera = None

        # This variable will store our score as an integer.
        self.score = 0

        # This variable will store the text for score that we will draw to the screen.
        self.score_text = None

        # Where is the right edge of the map?
        self.end_of_map = 0

        # Should we reset the score?
        self.reset_score = True

        # Shooting mechanics
        self.can_shoot = False
        self.shoot_timer = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.shoot_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True
            },
            "Moving Platforms": {
                "use_spatial_hash": False
            },
            "Ladders": {
                "use_spatial_hash": True
            }
        }

        map_path = LEVELS[self.level - 1]

        self.tile_map = arcade.load_tilemap(
            map_path,
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Create our Scene Based on the TileMap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        if "Enemies" not in self.scene:
            self.scene.add_sprite_list("Enemies")

        if "Coins" not in self.scene:
            self.scene.add_sprite_list("Coins")

        if "Moving Platforms" not in self.scene:
            self.scene.add_sprite_list("Moving Platforms")

        if "Ladders" not in self.scene:
            self.scene.add_sprite_list("Ladders")

        self.player_sprite = PlayerCharacter()
        # TEMPORAL PARA TEST
        self.player_sprite.has_double_jump = True

        self.player_sprite.has_dash = True
        self.player_sprite.dash_available = True

        self.player_sprite.has_wall_jump = True



        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # -- Enemies
        if "Enemies" in self.tile_map.object_lists:
            enemies_layer = self.tile_map.object_lists["Enemies"]

            for enemy_marker in enemies_layer:

                coordinates = self.tile_map.get_cartesian(
                    enemy_marker.shape[0],
                    enemy_marker.shape[1]
                )

                enemy_type = enemy_marker.properties["type"]

                if enemy_type == "robot":
                    enemy = RobotEnemy()

                elif enemy_type == "zombie":
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

                if "boundary_left" in enemy_marker.properties:
                    enemy.boundary_left = enemy_marker.properties["boundary_left"]

                if "boundary_right" in enemy_marker.properties:
                    enemy.boundary_right = enemy_marker.properties["boundary_right"]

                if "change_x" in enemy_marker.properties:
                    enemy.change_x = enemy_marker.properties["change_x"]

                self.scene.add_sprite("Enemies", enemy)

                for enemy_marker in enemies_layer:
                    coordinates = self.tile_map.get_cartesian(
                        enemy_marker.shape[0], enemy_marker.shape[1]
                    )
                    enemy_type = enemy_marker.properties["type"]
                    if enemy_type == "robot":
                        enemy = RobotEnemy()
                    elif enemy_type == "zombie":
                        enemy = ZombieEnemy()
                    enemy.center_x = math.floor(
                        coordinates[0] * TILE_SCALING * self.tile_map.tile_width
                    )
                    enemy.center_y = math.floor(
                        (coordinates[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
                    )
                    if "boundary_left" in enemy_marker.properties:
                        enemy.boundary_left = enemy_marker.properties["boundary_left"]
                    if "boundary_right" in enemy_marker.properties:
                        enemy.boundary_right = enemy_marker.properties["boundary_right"]
                    if "change_x" in enemy_marker.properties:
                        enemy.change_x = enemy_marker.properties["change_x"]

                    self.scene.add_sprite("Enemies", enemy)

        # Create a Platformer Physics Engine, this will handle moving our
        # player as well as collisions between the player sprite and
        # whatever SpriteList we specify for the walls.
        # It is important to supply static to the walls parameter. There is a
        # platforms parameter that is intended for moving platforms.
        # If a platform is supposed to move, and is added to the walls list,
        # it will not be moved.
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Platforms"],
            gravity_constant=GRAVITY,
            platforms=self.scene["Moving Platforms"],
            ladders=self.scene["Ladders"]
        )

        self.camera = arcade.camera.Camera2D()

        self.camera.viewport = arcade.LRBT(
            0,
            self.window.width,
            0,
            self.window.height
        )

        self.gui_camera = arcade.camera.Camera2D()

        # Reset the score if we should
        if self.reset_score:
            self.score = 0
        self.reset_score = True

        # Shooting mechanics
        self.can_shoot = False
        self.shoot_timer = 0

        # Initialize our arcade.Text object for score
        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)

        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Calculate the right edge of the map in pixels
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width)
        self.end_of_map *= self.tile_map.scaling

        # Add an empty bullet SpriteList to our scene
        self.scene.add_sprite_list("Bullets")

        self.window.background_color = self.tile_map.background_color

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

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate our camera before drawing
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        # Activate our GUI camera
        self.gui_camera.use()

        # Draw our Score
        self.score_text.draw()

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # --- WALL JUMP LOCK TIMER ---
        if self.player_sprite.wall_jump_lock_timer > 0:
            self.player_sprite.wall_jump_lock_timer -= delta_time

        # --- WALL SLIDE ---
        self.player_sprite.wall_sliding = False

        if self.player_sprite.has_wall_jump:

            touching_left_wall = False
            touching_right_wall = False

            # mover temporalmente para comprobar pared izquierda
            self.player_sprite.center_x -= 2
            if arcade.check_for_collision_with_list(
                self.player_sprite,
                self.scene["Platforms"]
            ):
                touching_left_wall = True

            # comprobar pared derecha
            self.player_sprite.center_x += 4
            if arcade.check_for_collision_with_list(
                self.player_sprite,
                self.scene["Platforms"]
            ):
                touching_right_wall = True

            # restaurar posición original
            self.player_sprite.center_x -= 2

            touching_wall = touching_left_wall or touching_right_wall

            on_ground = self.physics_engine.can_jump()

            moving_down = self.player_sprite.change_y <= 0

            pressing_wall = (
                (self.left_pressed and self.player_sprite.facing_direction == LEFT_FACING)
                or
                (self.right_pressed and self.player_sprite.facing_direction == RIGHT_FACING)
            )

            if (
                touching_wall
                and not on_ground
                and moving_down
                and pressing_wall
                and self.player_sprite.wall_jump_lock_timer <= 0
            ):

                self.player_sprite.wall_sliding = True

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
            self.player_sprite.double_jump_available = True
            self.player_sprite.dash_available = True
        else:
            self.player_sprite.coyote_timer = max(
                0, self.player_sprite.coyote_timer - delta_time
            )
        # --- Better Jump ---
        if not self.player_sprite.is_dashing:

            # Caída más rápida
            if self.player_sprite.change_y < 0:
                self.player_sprite.change_y -= GRAVITY * 0.8

            # Salto variable
            elif self.player_sprite.change_y > 0:
                if not self.player_sprite.jump_pressed:
                    self.player_sprite.change_y -= GRAVITY * 1.5

        # Update our characters animation state
        if self.physics_engine.is_on_ladder():
            self.player_sprite.climbing = True
        else:
            self.player_sprite.climbing = False

        if self.can_shoot:
            if self.shoot_pressed:
                self.play_sfx(self.shoot_sound)
                bullet = arcade.Sprite(
                    ":resources:images/space_shooter/laserBlue01.png",
                    scaling=0.8,
                )
                if self.player_sprite.facing_direction == RIGHT_FACING:
                    bullet.change_x = 12
                else:
                    bullet.change_x = -12

                bullet.center_x = self.player_sprite.center_x
                bullet.center_y = self.player_sprite.center_y

                self.scene.add_sprite("Bullets", bullet)
                self.can_shoot = False
        else:
            self.shoot_timer += 1
            if self.shoot_timer == 15:
                self.can_shoot = True
                self.shoot_timer = 0


        # Move the player using our physics engine
        self.physics_engine.update()
        
        # Actually trigger animation updates. We've added the Background and Coins layer
        # here as well. Our Tiled map has some animated tiles built-in, check out the flags
        # and torches on the map.
        self.scene.update_animation(
            delta_time,
            [
                "Coins",
                "Background",
                "Player",
                "Enemies"
            ]
        )

        self.scene.update(delta_time, ["Enemies", "Bullets"])

        # Keep enemies walking within their boundaries configured in Tiled
        for enemy in self.scene["Enemies"]:
            if enemy.right > enemy.boundary_right and enemy.change_x > 0:
                enemy.change_x *= -1
            elif enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1

        for bullet in self.scene["Bullets"]:
            hit_list = arcade.check_for_collision_with_lists(
                bullet,
                [
                    self.scene["Enemies"],
                    self.scene["Platforms"],
                    self.scene["Moving Platforms"]
                ]
            )

            if hit_list:
                bullet.remove_from_sprite_lists()

                for collision in hit_list:
                    if self.scene["Enemies"] in collision.sprite_lists:
                        collision.health -= 25

                        if collision.health <= 0:
                            collision.remove_from_sprite_lists()
                            self.score += 150

                        arcade.play_sound(
                            self.hit_sound,
                            volume=SETTINGS.sfx_volume
                        )

                return

            # Remove bullet if it leaves the map area.
            # Bullets only travel horizontally, so we only need to check left and right.
            if (bullet.right < 0) or (bullet.left > self.end_of_map):
                bullet.remove_from_sprite_lists()

        # See if we hit any coins
        player_collision_list = arcade.check_for_collision_with_lists(
            self.player_sprite,
            [
                self.scene["Coins"],
                self.scene["Enemies"]
            ]
        )

        for collision in player_collision_list:
            if self.scene["Enemies"] in collision.sprite_lists:
                self.play_sfx(self.gameover_sound)
                game_over = GameOverView()
                self.window.show_view(game_over)
                return
            else:
                # Our collision is a coin, remove it
                collision.remove_from_sprite_lists()
                self.play_sfx(self.collect_coin_sound)
                self.score += 75
                self.score_text.text = f"Score: {self.score}"

        # Center our camera on the player
        self.camera.position = self.player_sprite.position

        # Pasar de nivel
        if self.player_sprite.center_x >= self.end_of_map - 200:
            self.next_level()

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
            elif self.physics_engine.can_jump(y_distance=10) or self.player_sprite.coyote_timer > 0:
                
                # Salto normal
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.player_sprite.coyote_timer = 0

                arcade.play_sound(
                    self.jump_sound,
                    volume=SETTINGS.sfx_volume
                )

            elif (
                self.player_sprite.has_double_jump
                and self.player_sprite.double_jump_available
            ):
                # Doble salto
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

                # Gastar doble salto
                self.player_sprite.double_jump_available = False

                arcade.play_sound(
                    self.jump_sound,
                    volume=SETTINGS.sfx_volume
                )
            elif self.player_sprite.wall_sliding:

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
                # Evitar volver a agarrarse instantáneamente
                self.player_sprite.wall_jump_lock_timer = WALL_JUMP_LOCK_TIME

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

        if key == SETTINGS.key_pause:
            from views.pause_view import PauseMenuView
            self.window.show_view(PauseMenuView(self))
            return

        if key == SETTINGS.key_restart:
            new_game = GameView(level=self.level)
            self.window.show_view(new_game)
            return

        if key == SETTINGS.key_up:
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
                and not self.player_sprite.is_dashing
            ):

                self.player_sprite.is_dashing = True
                self.player_sprite.dash_available = False
                self.player_sprite.dash_timer = DASH_DURATION
                self.player_sprite.dash_cooldown_timer = DASH_COOLDOWN

                # Dirección del dash
                if self.player_sprite.facing_direction == RIGHT_FACING:
                    self.player_sprite.change_x = DASH_SPEED
                else:
                    self.player_sprite.change_x = -DASH_SPEED

                # Quitar velocidad vertical
                self.player_sprite.change_y = 0

        self.process_keychange()

    def on_key_release(self, key, modifiers):

        if key == SETTINGS.key_left:
            self.left_pressed = False

        elif key == SETTINGS.key_right:
            self.right_pressed = False

        elif key == SETTINGS.key_up:
            self.up_pressed = False
            self.player_sprite.jump_pressed = False

        elif key == SETTINGS.key_down:
            self.down_pressed = False

        if key == arcade.key.Q:
            self.shoot_pressed = False

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

    def play_sfx(self, sound):
        arcade.play_sound(
            sound,
            volume=SETTINGS.sfx_volume
        )

class GameOverView(arcade.View):
    def on_show_view(self):
        self.window.background_color = arcade.color.BLACK

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Game Over - Click to Restart",
            self.window.width // 2,
            self.window.height // 2,
            arcade.color.WHITE,
            30,
            anchor_x="center"
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)

    def on_resize(self, width, height):

        super().on_resize(width, height)

        self.camera.viewport = arcade.LRBT(
            0,
            width,
            0,
            height
        )

        
        self.gui_camera.viewport = arcade.LRBT(
            0,
            width,
            0,
            height
        )

    def next_level(self):

        next_level_number = self.level + 1

        # Si no hay más niveles
        if next_level_number > len(LEVELS):
            print("Juego completado")
            return

        # Crear nuevo nivel
        new_game = GameView(level=next_level_number, score=self.score)

        self.window.show_view(new_game)