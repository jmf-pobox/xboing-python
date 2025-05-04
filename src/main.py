#!/usr/bin/env python3
"""
XBoing - A classic breakout-style game.

This is the main entry point for the game. It initializes the game
engine and runs the main game loop.
"""

import logging
import os
import sys
import time

import pygame

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("xboing")

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.graphics import Renderer
from src.engine.input import InputManager
from src.engine.window import Window
from src.game.ball import Ball
from src.game.collision import CollisionSystem
from src.game.level_manager import LevelManager
from src.game.paddle import Paddle
from src.game.sprite_block import SpriteBlock, SpriteBlockManager
from src.utils.asset_loader import create_font
from src.utils.asset_paths import get_sounds_dir
from src.utils.layout import GameLayout

# Game constants - matching the original XBoing dimensions
PLAY_WIDTH = 495  # Original game's play area width
PLAY_HEIGHT = 580  # Original game's play area height
MAIN_WIDTH = 70  # Width of side panel in original
MAIN_HEIGHT = 130  # Height of additional UI elements

# Total window size
WINDOW_WIDTH = PLAY_WIDTH + MAIN_WIDTH  # 565
WINDOW_HEIGHT = PLAY_HEIGHT + MAIN_HEIGHT  # 710

# Game element sizes
PADDLE_WIDTH = 70  # Width of HUGE paddle in original (70px)
PADDLE_HEIGHT = 15  # Original paddle height (15px)
PADDLE_Y = WINDOW_HEIGHT - 40
BALL_RADIUS = 8  # Approximated from original game
MAX_BALLS = 3
BLOCK_WIDTH = 40  # Original block width
BLOCK_HEIGHT = 20  # Original block height
BLOCK_MARGIN = 7  # Original spacing (SPACE constant)
GAME_TITLE = "XBoing"


def main():
    """Main entry point for the game."""
    print("Starting XBoing initialization...")

    # Initialize the game window
    print("Creating window...")
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
    print("Window created.")
    renderer = Renderer(window.surface)
    print("Renderer initialized.")

    # Initialize input and managers
    input_manager = InputManager()

    # Initialize audio
    pygame.mixer.init()
    sounds = {}
    sound_volume = 0.7
    sound_enabled = True

    # Load available sound files from the sounds directory
    sounds_dir = get_sounds_dir()
    sound_files = {
        "boing": 0.7,  # Ball collision with blocks - signature sound
        "click": 0.5,  # UI actions
        "powerup": 0.6,  # Power-up collection
        "game_over": 0.8,  # Game over
        "ballshot": 0.6,  # Ball launch
        "balllost": 0.7,  # Ball lost
        "bomb": 0.8,  # Explosion
        "applause": 0.8,  # Level complete
        "bonus": 0.6,  # Bonus collected
        "paddle": 0.6,  # Ball hitting paddle - from original game
    }

    print(f"Loading sounds from: {sounds_dir}")

    # Load all sound files that exist
    for sound_name, volume in sound_files.items():
        sound_path = os.path.join(sounds_dir, f"{sound_name}.wav")
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(volume * sound_volume)
                sounds[sound_name] = sound
                print(f"Loaded sound: {sound_name}")
            except Exception as e:
                print(f"Failed to load sound {sound_name}: {e}")

    # Create a simplified sound playback function
    def play_sound(name):
        """Play a sound if it exists and sound is enabled"""
        if sound_enabled and name in sounds:
            sounds[name].play()

    # Print status
    print(f"XBoing: Audio system initialized with {len(sounds)} sounds")

    # Create the game layout
    layout = GameLayout(WINDOW_WIDTH, WINDOW_HEIGHT)

    # Load backgrounds using default paths
    layout.load_backgrounds()

    # Get play area rectangle
    play_rect = layout.get_play_rect()

    # Initialize collision system with play area dimensions
    collision_system = CollisionSystem(play_rect.width, play_rect.height)

    # Create game objects
    # Position the paddle using the same DIST_BASE value as the original game (30px from bottom)
    paddle_x = play_rect.x + (play_rect.width // 2) - (PADDLE_WIDTH // 2)
    paddle_y = play_rect.y + play_rect.height - Paddle.DIST_BASE
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)

    # Create ball array
    balls = []

    # Create sprite block manager positioned within the play area
    block_manager = SpriteBlockManager(
        play_rect.x, play_rect.y  # Offset all blocks by play area position
    )

    # Create level manager and set the block manager and layout
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)
    level_manager.set_layout(layout)

    # Set default background color (fallback)
    bg_color = (40, 44, 52)

    # Create fonts
    font = create_font(None, 24)
    small_font = create_font(None, 18)

    # Game state variables
    lives = 3
    score = 0
    level = 1
    sound_volume = 0.7  # Volume level (0.0 to 1.0)
    sound_enabled = True  # Sound on/off toggle
    game_over = False
    level_complete = False
    waiting_for_launch = True

    # Load the first level
    level_manager.load_level(level)

    # Sound volume is already set when loading the sounds

    # Function to create a new ball
    def create_new_ball():
        # The ball should be positioned relative to the paddle
        # which is already positioned correctly in the play area
        ball = Ball(
            paddle.rect.centerx,
            paddle.rect.top - BALL_RADIUS - 1,
            BALL_RADIUS,
            (255, 255, 255),
        )
        ball.stuck_to_paddle = True
        ball.paddle_offset = 0
        # Start with birth animation on new ball
        ball.birth_animation = True
        ball.animation_frame = 0
        ball.frame_counter = 0
        return ball

    # Create initial ball
    balls.append(create_new_ball())

    # Level is already loaded via level_manager above

    # Main game loop
    running = True
    last_time = time.time()

    while running:
        # Calculate delta time
        current_time = time.time()
        delta_ms = (current_time - last_time) * 1000
        last_time = current_time

        # Process input
        if not input_manager.update():
            running = False

        # Handle window events
        if not window.handle_events():
            running = False

        # If game over, only handle restart input
        if game_over:
            if input_manager.is_key_down(pygame.K_r):
                # Reset game
                game_over = False
                lives = 3
                score = 0
                level = 1
                play_rect = layout.get_play_rect()
                level_manager.load_level(level)
                balls.clear()
                balls.append(create_new_ball())
                waiting_for_launch = True

            # Draw game over screen
            renderer.clear(bg_color)

            # Draw the window layout
            layout.draw(window.surface)

            # Draw semi-transparent overlay for better text visibility, just in the play area
            play_rect = layout.get_play_rect()
            overlay = pygame.Surface(
                (play_rect.width, play_rect.height), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            window.surface.blit(overlay, (play_rect.x, play_rect.y))

            renderer.draw_text(
                "GAME OVER",
                font,
                (255, 50, 50),
                play_rect.centerx,
                play_rect.centery - 30,
                centered=True,
            )
            renderer.draw_text(
                f"Final Score: {score}",
                font,
                (255, 255, 255),
                play_rect.centerx,
                play_rect.centery + 10,
                centered=True,
            )
            renderer.draw_text(
                "Press R to restart",
                small_font,
                (200, 200, 200),
                play_rect.centerx,
                play_rect.centery + 50,
                centered=True,
            )

            # Update the display and continue
            window.update()
            continue

        # If level complete, set up the next level
        if level_complete and input_manager.is_key_down(pygame.K_SPACE):
            level += 1
            level_manager.get_next_level()  # Load the next level
            level_complete = False
            waiting_for_launch = True
            # Play sound for new level
            play_sound("click")

            # Create a new ball if needed
            if not balls:
                balls.append(create_new_ball())

        # Launch ball when space is pressed
        if waiting_for_launch and input_manager.is_key_down(pygame.K_SPACE):
            for ball in balls:
                ball.release_from_paddle()
            waiting_for_launch = False
            # Start the level timer when ball is launched
            level_manager.start_timer()
            # Play launch sound
            play_sound("ballshot")

        # Handle volume control
        if (
            input_manager.is_key_down(pygame.K_PLUS)
            or input_manager.is_key_down(pygame.K_KP_PLUS)
            or input_manager.is_key_down(pygame.K_EQUALS)
        ):
            # Increase volume
            sound_volume = min(1.0, sound_volume + 0.1)
            # Update volume for all sounds
            for sound_name, base_volume in sound_files.items():
                if sound_name in sounds:
                    sounds[sound_name].set_volume(
                        base_volume * (sound_volume if sound_enabled else 0)
                    )
            play_sound("click")

        if input_manager.is_key_down(pygame.K_MINUS) or input_manager.is_key_down(
            pygame.K_KP_MINUS
        ):
            # Decrease volume
            sound_volume = max(0.0, sound_volume - 0.1)
            # Update volume for all sounds
            for sound_name, base_volume in sound_files.items():
                if sound_name in sounds:
                    sounds[sound_name].set_volume(
                        base_volume * (sound_volume if sound_enabled else 0)
                    )
            play_sound("click")

        if input_manager.is_key_down(pygame.K_m):
            # Toggle sound on/off
            sound_enabled = not sound_enabled
            # Update volume for all sounds
            for sound_name, base_volume in sound_files.items():
                if sound_name in sounds:
                    sounds[sound_name].set_volume(
                        base_volume * (sound_volume if sound_enabled else 0)
                    )
            # Always play a click when enabling sound
            if sound_enabled:
                play_sound("click")

        # Update paddle movement based on input
        paddle_direction = 0
        if input_manager.is_key_pressed(pygame.K_LEFT):
            paddle_direction = -1
        elif input_manager.is_key_pressed(pygame.K_RIGHT):
            paddle_direction = 1

        # Update paddle position using play window boundaries
        play_rect = layout.get_play_rect()
        paddle.set_direction(paddle_direction)
        paddle.update(delta_ms, play_rect.width, play_rect.x)

        # Mouse control (convert global mouse position to play area position)
        mouse_pos = input_manager.get_mouse_position()
        if input_manager.is_mouse_button_pressed(0):  # Left mouse button
            # Calculate paddle position relative to play area
            local_x = mouse_pos[0] - play_rect.x - PADDLE_WIDTH // 2
            paddle.move_to(local_x, play_rect.width, play_rect.x)

        # Update blocks
        block_manager.update(delta_ms)

        # Update level timer if game is active
        if not waiting_for_launch and not game_over and not level_complete:
            level_manager.update(delta_ms)

        # Update ball positions and check collisions
        active_balls = []
        for ball in balls:
            # Update ball using play window boundaries
            play_rect = layout.get_play_rect()
            is_active, hit_paddle, hit_wall = ball.update(
                delta_ms,
                play_rect.width,  # Width of play area instead of window width
                play_rect.height,  # Height of play area instead of window height
                paddle,
                play_rect.x,  # X offset of play area
                play_rect.y,  # Y offset of play area
            )

            if is_active:
                # Check collisions with blocks
                points, broken, effects = block_manager.check_collisions(ball)
                score += points

                # Play sounds for collisions
                if broken > 0:
                    # Play boing sound for block hits at normal volume
                    play_sound("boing")

                # Handle special block effects
                for effect in effects:
                    if effect == SpriteBlock.TYPE_EXTRABALL:
                        # Add an extra ball
                        new_ball = Ball(ball.x, ball.y, BALL_RADIUS, (255, 255, 255))
                        # Give the new ball a different velocity
                        new_ball.vx = -ball.vx
                        new_ball.vy = ball.vy
                        balls.append(new_ball)
                        play_sound("powerup")

                    elif effect == SpriteBlock.TYPE_MULTIBALL:
                        # Add multiple balls
                        for i in range(2):  # Add 2 more balls
                            new_ball = Ball(
                                ball.x, ball.y, BALL_RADIUS, (255, 255, 255)
                            )
                            # Give each new ball a different velocity
                            angle = i * 3.14159 / 2  # 90 degrees apart
                            speed = (ball.vx**2 + ball.vy**2) ** 0.5
                            new_ball.vx = speed * (ball.vx / speed) * 0.8
                            new_ball.vy = speed * (ball.vy / speed) * 0.8
                            balls.append(new_ball)
                        play_sound("powerup")

                    elif effect == SpriteBlock.TYPE_BOMB:
                        # Explosion effect - would destroy neighboring blocks
                        play_sound("bomb")

                    elif effect in [
                        SpriteBlock.TYPE_PAD_EXPAND,
                        SpriteBlock.TYPE_PAD_SHRINK,
                    ]:
                        # Change paddle size
                        if effect == SpriteBlock.TYPE_PAD_EXPAND:
                            paddle.width = min(
                                PADDLE_WIDTH * 1.5, PADDLE_WIDTH * 2
                            )  # Expand by 50%
                        else:
                            paddle.width = max(
                                PADDLE_WIDTH * 0.5, PADDLE_WIDTH / 2
                            )  # Shrink by 50%
                        # Update paddle rectangle
                        paddle.rect.width = paddle.width
                        play_sound("powerup")

                    elif effect == SpriteBlock.TYPE_TIMER:
                        # Add time to the level timer
                        level_manager.add_time(20)  # Add 20 seconds
                        play_sound("powerup")

                # Play paddle hit sound if paddle was hit
                if hit_paddle:
                    # Play the original paddle hit sound
                    play_sound("paddle")

                # Play wall hit sound if wall was hit (at lower volume)
                if hit_wall:
                    # In the original game, the wall collision used the boing sound
                    # but at a much lower volume (10 compared to normal 50-100)
                    # We'll use a reduced volume boing sound for wall collisions
                    if "boing" in sounds:
                        # Play at reduced volume (original used 10% of normal)
                        temp_vol = sounds["boing"].get_volume()
                        sounds["boing"].set_volume(
                            temp_vol * 0.2
                        )  # ~20% of normal volume
                        sounds["boing"].play()
                        # Restore normal volume after playing
                        sounds["boing"].set_volume(temp_vol)

                active_balls.append(ball)
            else:
                # Ball lost sound
                play_sound("balllost")

        # Update active balls list
        balls = active_balls

        # If all balls are lost, decrement lives
        if len(balls) == 0:
            lives -= 1

            if lives > 0:
                # Create a new ball
                balls.append(create_new_ball())
                waiting_for_launch = True
                # Stop the timer while waiting for launch
                level_manager.stop_timer()
            else:
                # Game over
                game_over = True
                # Stop the timer
                level_manager.stop_timer()
                # Play game over sound
                play_sound("game_over")

        # Check if level is complete (all breakable blocks destroyed)
        if level_manager.is_level_complete() and not level_complete:
            level_complete = True
            # Play level complete sound
            play_sound("applause")

        # Clear the screen and draw window layout
        renderer.clear(bg_color)
        layout.draw(window.surface)

        # Draw the blocks
        block_manager.draw(window.surface)

        # Draw the paddle
        paddle.draw(window.surface)

        # Draw all balls
        for ball in balls:
            ball.draw(window.surface)

        # Draw the walls inside the play area
        play_rect = layout.get_play_rect()
        wall_color = (100, 100, 100)

        pygame.draw.rect(
            window.surface,
            wall_color,
            pygame.Rect(play_rect.x, play_rect.y, play_rect.width, 2),
        )  # Top
        pygame.draw.rect(
            window.surface,
            wall_color,
            pygame.Rect(play_rect.x, play_rect.y, 2, play_rect.height),
        )  # Left
        pygame.draw.rect(
            window.surface,
            wall_color,
            pygame.Rect(
                play_rect.x + play_rect.width - 2, play_rect.y, 2, play_rect.height
            ),
        )  # Right

        # Draw UI elements in their respective windows
        score_rect = layout.get_score_rect()
        level_rect = layout.get_level_rect()
        message_rect = layout.get_message_rect()

        # Score area
        renderer.draw_text(
            f"Lives: {lives}",
            font,
            (255, 255, 255),
            score_rect.x + 20,
            score_rect.y + 15,
        )
        renderer.draw_text(
            f"Score: {score}",
            font,
            (255, 255, 255),
            score_rect.x + score_rect.width - 80,
            score_rect.y + 15,
        )

        # Level info
        level_info = level_manager.get_level_info()
        renderer.draw_text(
            f"Level: {level_info['level_num']}",
            font,
            (255, 255, 255),
            level_rect.centerx,
            level_rect.y + 15,
            centered=True,
        )
        renderer.draw_text(
            f"{level_info['title']}",
            small_font,
            (200, 200, 255),
            level_rect.centerx,
            level_rect.y + 40,
            centered=True,
        )

        # Time bonus if active
        if not waiting_for_launch and not game_over and not level_complete:
            time_color = (255, 255, 0)  # Yellow by default
            time_remaining = level_manager.get_time_remaining()

            # Make time red if running low
            if time_remaining < 10:
                time_color = (255, 50, 50)

            renderer.draw_text(
                f"Time: {time_remaining}",
                small_font,
                time_color,
                level_rect.centerx,
                level_rect.y + 60,
                centered=True,
            )

        # Original XBoing doesn't show these helper messages, so we've removed:
        # - Sound status
        # - "Press SPACE to launch" instruction
        # - Control instructions

        # Draw level complete message
        if level_complete:
            # Draw level complete overlay in play area
            level_overlay = pygame.Surface(
                (play_rect.width, play_rect.height), pygame.SRCALPHA
            )
            level_overlay.fill((0, 0, 0, 150))  # Semi-transparent black
            window.surface.blit(level_overlay, (play_rect.x, play_rect.y))

            renderer.draw_text(
                "LEVEL COMPLETE!",
                font,
                (50, 255, 50),
                play_rect.centerx,
                play_rect.centery - 30,
                centered=True,
            )
            renderer.draw_text(
                "Press SPACE for next level",
                small_font,
                (200, 200, 200),
                play_rect.centerx,
                play_rect.centery + 10,
                centered=True,
            )

        # Update the display
        window.update()

    # Clean up
    window.cleanup()
    pygame.mixer.quit()


if __name__ == "__main__":
    main()
