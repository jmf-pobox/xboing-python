#!/usr/bin/env python3
"""
XBoing - A classic breakout-style game.

This is the main entry point for the game. It initializes the game
engine and runs the main game loop.
"""

import logging
import time

import pygame
from engine.audio_manager import AudioManager
from engine.events import (
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    BlockHitEvent,
    BombExplodedEvent,
    BonusCollectedEvent,
    GameOverEvent,
    MessageChangedEvent,
    PaddleHitEvent,
    PowerUpCollectedEvent,
    UIButtonClickEvent,
    WallHitEvent,
)
from engine.graphics import Renderer
from engine.input import InputManager
from engine.window import Window
from game.ball import Ball
from game.game_state import GameState
from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlock, SpriteBlockManager
from ui.bottom_bar_view import BottomBarView
from ui.content_view_manager import ContentViewManager
from ui.game_view import GameView
from ui.game_over_view import GameOverView
from ui.instructions_view import InstructionsView
from ui.level_display import LevelDisplay
from ui.lives_display import LivesDisplayComponent
from ui.message_display import MessageDisplay
from ui.score_display import ScoreDisplay
from ui.special_display import SpecialDisplay
from ui.timer_display import TimerDisplay
from ui.top_bar_view import TopBarView
from utils.asset_loader import create_font
from utils.asset_paths import get_sounds_dir
from utils.digit_display import DigitDisplay
from utils.event_bus import EventBus
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

# Definition of event to sound mapping
event_sound_map = {
    BlockHitEvent: "boing",
    UIButtonClickEvent: "click",
    PowerUpCollectedEvent: "powerup",
    GameOverEvent: "game_over",
    BallShotEvent: "ballshot",
    BallLostEvent: "balllost",
    BombExplodedEvent: "bomb",
    ApplauseEvent: "applause",
    BonusCollectedEvent: "bonus",
    PaddleHitEvent: "paddle",
    WallHitEvent: "boing",  # Wall hit uses boing sound, can be handled specially if needed
}

def main():
    """Main entry point for the game."""
    print("Starting XBoing initialization...")

    # --- Initialization: Event bus, game state, audio, window, input, layout ---
    event_bus = EventBus()
    game_state = GameState(event_bus)
    pygame.mixer.init()
    audio_manager = AudioManager(event_bus, sound_dir=get_sounds_dir(), event_sound_map=event_sound_map)
    audio_manager.load_sounds_from_map()
    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
    renderer = Renderer(window.surface)
    input_manager = InputManager()
    layout = GameLayout(WINDOW_WIDTH, WINDOW_HEIGHT)
    layout.load_backgrounds()
    play_rect = layout.get_play_rect()  # Only used for paddle/block_manager init below

    # --- Create game objects: paddle, balls, blocks, level manager ---
    paddle_x = play_rect.x + (play_rect.width // 2) - (PADDLE_WIDTH // 2)
    paddle_y = play_rect.y + play_rect.height - Paddle.DIST_BASE
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    balls = []
    block_manager = SpriteBlockManager(play_rect.x, play_rect.y)
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)
    level_manager.set_layout(layout)
    bg_color = (40, 44, 52)

    # --- Fonts and UI components ---
    font = create_font(None, 24)
    small_font = create_font(None, 18)
    ui_font = create_font(None, 34)
    message_font = create_font(None, 28)
    special_font = create_font(None, 16)
    instructions_headline_font = create_font(None, 26)
    instructions_text_font = create_font(None, 21)
    digit_display = DigitDisplay()
    lives_display = LivesDisplay()
    score_display = ScoreDisplay(event_bus, layout, digit_display, x=70, width=6)
    lives_display_component = LivesDisplayComponent(event_bus, layout, lives_display, x=365, max_lives=3)
    level_display_component = LevelDisplay(event_bus, layout, digit_display, x=510)
    timer_display_component = TimerDisplay(event_bus, layout, renderer, ui_font)
    message_display_component = MessageDisplay(event_bus, layout, renderer, message_font)
    special_display_component = SpecialDisplay(event_bus, layout, renderer, special_font)

    # --- ContentViewManager and content views ---
    content_view_manager = ContentViewManager()
    # --- Game View ---
    game_view = GameView(layout, block_manager, paddle, balls, renderer)
    content_view_manager.register_view('game', game_view)
    content_view_manager.set_view('game')
    # --- Instructions View ---
    instructions_view = InstructionsView(layout, renderer, font, instructions_headline_font, instructions_text_font)
    content_view_manager.register_view('instructions', instructions_view)
    # --- Game Over View ---
    game_over_view = GameOverView(
        layout,
        renderer,
        font,
        small_font,
        lambda: game_state.score,
        reset_game_callback=None  # Will be set after definition
    )
    content_view_manager.register_view('game_over', game_over_view)

    # --- Game state variables ---
    level_complete = False
    waiting_for_launch = True

    # --- Fire initial events for UI state ---
    game_state.set_score(0)
    game_state.set_lives(3)
    game_state.set_level(1)
    level_manager.load_level(game_state.level)
    game_state.set_timer(level_manager.get_time_remaining())
    level_info = level_manager.get_level_info()
    level_title = level_info['title']
    event_bus.fire(MessageChangedEvent(level_title, color=(0,255,0), alignment='left'))

    # --- Helper: create a new ball stuck to the paddle ---
    def create_new_ball():
        ball = Ball(
            paddle.rect.centerx,
            paddle.rect.top - BALL_RADIUS - 1,
            BALL_RADIUS,
            (255, 255, 255),
        )
        ball.stuck_to_paddle = True
        ball.paddle_offset = 0
        ball.birth_animation = True
        ball.animation_frame = 0
        ball.frame_counter = 0
        return ball

    # --- Start with one ball ---
    def reset_game():
        logger.info("reset_game called: restarting game state and returning to gameplay view.")
        game_state.restart()
        logger.info(f"After restart: game_state.is_game_over() = {game_state.is_game_over()}")
        play_rect = layout.get_play_rect()
        level_manager.load_level(game_state.level)
        balls.clear()
        balls.append(create_new_ball())
        game_view.balls = balls
        nonlocal waiting_for_launch
        waiting_for_launch = True
        content_view_manager.set_view('game')
    game_over_view.reset_game = reset_game

    top_bar_view = TopBarView(
        score_display,
        lives_display_component,
        level_display_component,
        timer_display_component,
        message_display_component,
        special_display_component
    )

    bottom_bar_view = BottomBarView(
        message_display_component,
        special_display_component,
        timer_display_component
    )

    # --- Game loop ---
    balls.append(create_new_ball())
    running = True
    last_time = time.time()

    while running:
        # --- Timing and input ---
        current_time = time.time()
        delta_ms = (current_time - last_time) * 1000
        last_time = current_time
        events = pygame.event.get()  # Only call once per frame!
        if not input_manager.update(events):
            running = False
        if not window.handle_events(events):
            running = False
        # Route key events to current content view
        for event in events:
            logger.debug(f"Main loop: routing event {event} to current view: {content_view_manager.current_name}")
            if content_view_manager.current_view is not None:
                logger.debug(f"Routing event {event} to current view: {content_view_manager.current_name}")
                content_view_manager.current_view.handle_event(event)

        # --- Game over screen logic ---
        if game_state.is_game_over():
            if content_view_manager.current_name != 'game_over':
                logger.info("Switching to game_over view.")
                content_view_manager.set_view('game_over')
            logger.debug("Game over state detected. Drawing only game over overlay.")
            renderer.clear(bg_color)
            layout.draw(window.surface)
            content_view_manager.draw(window.surface)
            window.update()
            continue

        # --- Level complete logic ---
        if level_complete and input_manager.is_key_down(pygame.K_SPACE):
            game_state.set_level(game_state.level + 1)
            level_manager.get_next_level()
            level_complete = False
            waiting_for_launch = True
            event_bus.fire(UIButtonClickEvent())
            level_info = level_manager.get_level_info()
            level_title = level_info['title']
            event_bus.fire(MessageChangedEvent(level_title, color=(0,255,0), alignment='left'))
            if not balls:
                balls.append(create_new_ball())

        # --- Ball launch logic ---
        if waiting_for_launch and input_manager.is_key_down(pygame.K_SPACE):
            for ball in balls:
                ball.release_from_paddle()
            waiting_for_launch = False
            level_manager.start_timer()
            event_bus.fire(BallShotEvent())
            level_info = level_manager.get_level_info()
            level_title = level_info['title']
            event_bus.fire(MessageChangedEvent(level_title, color=(0,255,0), alignment='left'))

        # --- Volume and sound controls ---
        if (
            input_manager.is_key_down(pygame.K_PLUS)
            or input_manager.is_key_down(pygame.K_KP_PLUS)
            or input_manager.is_key_down(pygame.K_EQUALS)
        ):
            new_volume = min(1.0, audio_manager.get_volume() + 0.1)
            audio_manager.set_volume(new_volume)
            event_bus.fire(UIButtonClickEvent())
        if input_manager.is_key_down(pygame.K_MINUS) or input_manager.is_key_down(pygame.K_KP_MINUS):
            new_volume = max(0.0, audio_manager.get_volume() - 0.1)
            audio_manager.set_volume(new_volume)
            event_bus.fire(UIButtonClickEvent())
        if input_manager.is_key_down(pygame.K_m):
            if audio_manager.is_muted():
                audio_manager.unmute()
                event_bus.fire(UIButtonClickEvent())
            else:
                audio_manager.mute()

        # --- Instructions view toggle (Shift + / for '?') ---
        if (
            content_view_manager.current_name != 'instructions'
            and input_manager.is_key_down(pygame.K_SLASH)
            and (pygame.key.get_mods() & pygame.KMOD_SHIFT)
        ):
            content_view_manager.set_view('instructions')
        elif content_view_manager.current_name == 'instructions' and input_manager.is_key_down(pygame.K_SPACE):
            content_view_manager.set_view('game')

        # --- Gameplay update (only if not in instructions view) ---
        if content_view_manager.current_name != 'instructions':
            # Paddle movement and input
            paddle_direction = 0
            if input_manager.is_key_pressed(pygame.K_LEFT):
                paddle_direction = -1
            elif input_manager.is_key_pressed(pygame.K_RIGHT):
                paddle_direction = 1
            play_rect = layout.get_play_rect()
            paddle.set_direction(paddle_direction)
            paddle.update(delta_ms, play_rect.width, play_rect.x)
            # Mouse paddle control
            mouse_pos = input_manager.get_mouse_position()
            if input_manager.is_mouse_button_pressed(0):
                local_x = mouse_pos[0] - play_rect.x - PADDLE_WIDTH // 2
                paddle.move_to(local_x, play_rect.width, play_rect.x)
            # Block and timer updates
            block_manager.update(delta_ms)
            if not waiting_for_launch and not game_state.is_game_over() and not level_complete:
                level_manager.update(delta_ms)
                game_state.set_timer(level_manager.get_time_remaining())
            # Ball update and collision
            active_balls = []
            for ball in balls:
                play_rect = layout.get_play_rect()
                is_active, hit_paddle, hit_wall = ball.update(
                    delta_ms,
                    play_rect.width,
                    play_rect.height,
                    paddle,
                    play_rect.x,
                    play_rect.y,
                )
                if is_active:
                    # Check collisions with blocks
                    points, broken, effects = block_manager.check_collisions(ball)
                    if points != 0:
                        game_state.add_score(points)

                    # Play sounds for collisions
                    if broken > 0:
                        # Play boing sound for block hits at normal volume
                        event_bus.fire(BlockHitEvent())

                    # Handle special block effects
                    for effect in effects:
                        if effect == SpriteBlock.TYPE_EXTRABALL:
                            # Add an extra ball
                            new_ball = Ball(ball.x, ball.y, BALL_RADIUS, (255, 255, 255))
                            # Give the new ball a different velocity
                            new_ball.vx = -ball.vx
                            new_ball.vy = ball.vy
                            balls.append(new_ball)
                            event_bus.fire(PowerUpCollectedEvent())

                        elif effect == SpriteBlock.TYPE_MULTIBALL:
                            # Add multiple balls
                            for _ in range(2):  # Add 2 more balls
                                new_ball = Ball(
                                    ball.x, ball.y, BALL_RADIUS, (255, 255, 255)
                                )
                                # Give each new ball a different velocity
                                speed = (ball.vx**2 + ball.vy**2) ** 0.5
                                new_ball.vx = speed * (ball.vx / speed) * 0.8
                                new_ball.vy = speed * (ball.vy / speed) * 0.8
                                balls.append(new_ball)
                            event_bus.fire(PowerUpCollectedEvent())

                        elif effect == SpriteBlock.TYPE_BOMB:
                            # Explosion effect - would destroy neighboring blocks
                            event_bus.fire(BombExplodedEvent())

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
                            event_bus.fire(PowerUpCollectedEvent())

                        elif effect == SpriteBlock.TYPE_TIMER:
                            # Add time to the level timer
                            level_manager.add_time(20)  # Add 20 seconds
                            event_bus.fire(PowerUpCollectedEvent())

                    # Play paddle hit sound if paddle was hit
                    if hit_paddle:
                        # Play the original paddle hit sound
                        event_bus.fire(PaddleHitEvent())

                    # Play wall hit sound if wall was hit (at lower volume)
                    if hit_wall:
                        # In the original game, the wall collision used the boing sound
                        # but at a much lower volume (10 compared to normal 50-100)
                        # We'll use a reduced volume boing sound for wall collisions
                        if "boing" in event_sound_map:
                            # Play at reduced volume (original used 10% of normal)
                            temp_vol = audio_manager.get_volume()
                            audio_manager.set_volume(
                                temp_vol * 0.2
                            )  # ~20% of normal volume
                            event_bus.fire(WallHitEvent())
                            # Restore normal volume after playing
                            audio_manager.set_volume(temp_vol)

                    active_balls.append(ball)
                else:
                    # Ball lost sound
                    event_bus.fire(BallLostEvent())

            # Update active balls list
            balls = active_balls
            game_view.balls = balls

            # If all balls are lost, decrement lives
            if len(balls) == 0:
                game_state.lose_life()

                if game_state.lives > 0:
                    # Create a new ball
                    balls.append(create_new_ball())
                    game_view.balls = balls
                    waiting_for_launch = True
                    # Stop the timer while waiting for launch
                    level_manager.stop_timer()
                else:
                    # Game over
                    game_state.set_game_over(True)
                    # Stop the timer
                    level_manager.stop_timer()
                    # Play game over sound
                    event_bus.fire(GameOverEvent())
                # Show 'Balls Terminated!' message only if lives remain
                if game_state.lives > 0:
                    event_bus.fire(MessageChangedEvent("Balls Terminated!", color=(0,255,0), alignment='left'))

            # Check if level is complete (all breakable blocks destroyed)
            if level_manager.is_level_complete() and not level_complete:
                level_complete = True
                # Play level complete sound
                event_bus.fire(ApplauseEvent())

            # === DEBUG: Blow up all blocks and advance level with X key ===
            if input_manager.is_key_down(pygame.K_x) and not game_state.is_game_over() and not level_complete:
                block_manager.blocks.clear()
                level_complete = True
                event_bus.fire(BombExplodedEvent())
            # === END DEBUG ===

        # Drawing is always done, regardless of instructions_active
        # Clear the screen and draw window layout
        renderer.clear(bg_color)
        layout.draw(window.surface)

        # Draw the current content view (gameplay, instructions, etc.)
        content_view_manager.draw(window.surface)

        # Draw all elements in the top bar
        top_bar_view.draw(window.surface)

        # Draw all elements in the bottom bar
        bottom_bar_view.draw(window.surface)

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


if __name__ == "__main__":
    main()
    