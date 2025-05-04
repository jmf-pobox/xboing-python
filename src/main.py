#!/usr/bin/env python3
"""
XBoing - A classic breakout-style game.

This is the main entry point for the game. It initializes the game
engine and runs the main game loop.
"""

import logging
import os
import time

import pygame
from engine.graphics import Renderer
from engine.input import InputManager
from engine.window import Window
from game.ball import Ball
from game.collision import CollisionSystem
from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlock, SpriteBlockManager
from utils.asset_loader import create_font
from utils.asset_paths import get_sounds_dir
from utils.digit_display import DigitDisplay
from utils.layout import GameLayout
from utils.lives_display import LivesDisplay

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("xboing")

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
GAME_TITLE = "- XBoing II -"


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
    
    # Create UI display objects
    digit_display = DigitDisplay()
    lives_display = LivesDisplay()

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
                play_rect.centery - 60,
                centered=True,
            )
            
            # Draw "FINAL SCORE" text
            renderer.draw_text(
                "FINAL SCORE",
                small_font,
                (255, 255, 255),
                play_rect.centerx,
                play_rect.centery - 20,
                centered=True,
            )
            
            # Render final score with LED digits
            score_display = digit_display.render_number(score, spacing=2, scale=1.0)
            
            # Center the score in the play area
            score_x = play_rect.centerx - (score_display.get_width() // 2)
            score_y = play_rect.centery + 10
            window.surface.blit(score_display, (score_x, score_y))
            
            renderer.draw_text(
                "Press R to restart",
                small_font,
                (200, 200, 200),
                play_rect.centerx,
                play_rect.centery + 70,
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
                            paddle.width = int(min(
                                PADDLE_WIDTH * 1.5, PADDLE_WIDTH * 2
                            ))  # Expand by 50%
                        else:
                            paddle.width = int(max(
                                PADDLE_WIDTH * 0.5, PADDLE_WIDTH / 2
                            ))  # Shrink by 50%
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

        # === DEBUG: Blow up all blocks and advance level with X key ===
        if input_manager.is_key_down(pygame.K_x) and not game_over and not level_complete:
            block_manager.blocks.clear()
            level_complete = True
            play_sound("bomb")
        # === END DEBUG ===

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

        # Get UI rectangles for drawing elements
        score_rect = layout.get_score_rect()
        level_rect = layout.get_level_rect()
        message_rect = layout.get_message_rect()
        
        # Define the UI layout based on the original XBoing-C.png screenshot
        # Element ordering in top bar (from right to left):
        # 1. Level (LED digits) at far right
        # 2. Lives (ball images) to the left of level
        # 3. Score (LED digits) at left
        # 4. Level name ("Genesis") in bottom left
        # 5. Timer in bottom right with normal yellow font
        
        # Get the level info and render displays
        level_info = level_manager.get_level_info()
        level_num = level_info['level_num']
        level_title = level_info['title']
        
        # Simple approach - render the numbers directly
        score_display = digit_display.render_number(score, spacing=2, scale=1.0)
        level_display = digit_display.render_number(level_num, spacing=2, scale=1.0)
        
        # Render lives using ball images
        lives_surf = lives_display.render(lives, spacing=10, scale=1.0, max_lives=3)
        
        # Calculate vertical position - center in top bar
        top_bar_y = score_rect.y + (score_rect.height - score_display.get_height()) // 2
        
        # ********* SIMPLER DIRECT APPROACH ***********
        # We'll directly set hard-coded positions to match original
        
        # From the debug log, we have:
        # Score rect: x=35, y=10, width=224, height=42
        
        level_x = 510
        lives_x = 525 - 100 - 60 
        score_x = 220
        
        # Create debug log file
        debug_log = open("/tmp/xboing_ui_debug.log", "w")
        
        # Log detailed UI information
        debug_log.write("=== XBOING UI DEBUG LOG ===\n\n")
        
        # Log window dimensions
        debug_log.write("WINDOW DIMENSIONS:\n")
        debug_log.write(f"Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}\n")
        debug_log.write(f"Score rect: x={score_rect.x}, y={score_rect.y}, width={score_rect.width}, height={score_rect.height}\n")
        debug_log.write(f"Level rect: x={level_rect.x}, y={level_rect.y}, width={level_rect.width}, height={level_rect.height}\n")
        debug_log.write(f"Play rect: x={play_rect.x}, y={play_rect.y}, width={play_rect.width}, height={play_rect.height}\n\n")
        
        # Log element details 
        debug_log.write("DISPLAY ELEMENTS:\n")
        debug_log.write(f"Score value: {score}\n")
        debug_log.write(f"Level value: {level_num}\n")
        debug_log.write(f"Lives count: {lives}\n\n")
        
        # Log element dimensions
        debug_log.write("ELEMENT DIMENSIONS:\n")
        debug_log.write(f"Score display: width={score_display.get_width()}, height={score_display.get_height()}\n")
        debug_log.write(f"Lives display: width={lives_surf.get_width()}, height={lives_surf.get_height()}\n")
        debug_log.write(f"Level display: width={level_display.get_width()}, height={level_display.get_height()}\n\n")
        
        # Log positioning details
        debug_log.write("ELEMENT POSITIONS:\n")
        debug_log.write(f"Score position: x={score_x}, y={top_bar_y}\n")
        debug_log.write(f"Lives position: x={lives_x}, y={top_bar_y}\n")
        debug_log.write(f"Level position: x={level_x}, y={top_bar_y}\n\n")
        
        # Log right-alignment details
        debug_log.write("RIGHT EDGE POSITIONS:\n")
        debug_log.write(f"Score right edge: {score_x + score_display.get_width()}\n")
        debug_log.write(f"Lives right edge: {lives_x + lives_surf.get_width()}\n")
        debug_log.write(f"Level right edge: {level_x + level_display.get_width()}\n\n")
        
        # Close debug log
        debug_log.close()
        
        # Draw all elements in the top bar
        window.surface.blit(score_display, (score_x, top_bar_y))
        window.surface.blit(lives_surf, (lives_x, top_bar_y))
        window.surface.blit(level_display, (level_x, top_bar_y))
        
        # Move level title to bottom bar (left-justified in message window)
        # Get message window rect
        message_rect = layout.get_message_rect()
        renderer.draw_text(
            level_title,
            small_font,
            (0, 255, 0),  # Green color like "Balls Terminated!" in original
            message_rect.x + 10,  # Left margin
            message_rect.y + (message_rect.height // 2),  # Vertically centered
            centered=False,  # Left-aligned
        )
        
        # Get a reference to the time window in the bottom right
        time_rect = layout.time_window.rect.rect
        
        # Time bonus display if active - use regular font with yellow color
        if not waiting_for_launch and not game_over and not level_complete:
            time_remaining = level_manager.get_time_remaining()
            
            # Format time as MM:SS
            minutes = time_remaining // 60
            seconds = time_remaining % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Create a large font for the timer
            timer_font = create_font(None, 32)  # Larger font for timer
            timer_color = (255, 255, 0)  # Bright yellow
            
            # Render and position in the bottom right corner
            renderer.draw_text(
                time_str,
                timer_font,
                timer_color,
                time_rect.x + (time_rect.width // 2),
                time_rect.y + (time_rect.height // 2),
                centered=True,  # Center in the time window
            )
            
            # Add a colored background when time is running low
            if time_remaining < 10:
                # Create a rectangle behind the timer text
                time_text_width = timer_font.size(time_str)[0]
                time_text_height = timer_font.size(time_str)[1]
                time_bg_rect = pygame.Rect(
                    time_rect.x + (time_rect.width // 2) - (time_text_width // 2) - 5,
                    time_rect.y + (time_rect.height // 2) - (time_text_height // 2) - 5,
                    time_text_width + 10,
                    time_text_height + 10
                )
                pygame.draw.rect(window.surface, (255, 50, 50), time_bg_rect)  # Red background
                
                # Re-render text on top of red background
                renderer.draw_text(
                    time_str,
                    timer_font,
                    timer_color,
                    time_rect.x + (time_rect.width // 2),
                    time_rect.y + (time_rect.height // 2),
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
