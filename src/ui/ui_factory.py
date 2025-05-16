from renderers.digit_renderer import DigitRenderer
from renderers.lives_renderer import LivesRenderer
from ui.bottom_bar_view import BottomBarView
from ui.game_over_view import GameOverView
from ui.game_view import GameView
from ui.instructions_view import InstructionsView
from ui.level_complete_view import LevelCompleteView
from ui.level_display import LevelDisplay
from ui.lives_display import LivesDisplayComponent
from ui.message_display import MessageDisplay
from ui.score_display import ScoreDisplay
from ui.special_display import SpecialDisplay
from ui.timer_display import TimerDisplay
from ui.top_bar_view import TopBarView
from utils.asset_loader import create_font


class UIFactory:
    """
    Factory for creating and wiring up all UI components, views, and bars for XBoing.
    This centralizes UI instantiation and layout logic, keeping main.py clean and focused
    on high-level orchestration. All dependencies must be passed in; no direct imports
    of game state or event bus should occur here.
    """

    @staticmethod
    def create_ui_components(
        game_state,
        layout,
        renderer,
        balls,
        paddle,
        block_manager,
        level_manager,
        instructions_view=None,
    ):
        """
        Construct and return all UI components, views, and bars.
        Args:
            game_state: The game state instance
            layout: The GameLayout instance
            renderer: The main Renderer instance
            balls: The list of Ball objects
            paddle: The Paddle instance
            block_manager: The SpriteBlockManager instance
            level_manager: The LevelManager instance
            instructions_view: The InstructionsView instance (optional)
        Returns:
            dict: A dictionary containing all created UI elements (views, top_bar, bottom_bar, etc.)
        """
        # Fonts
        font = create_font(24)
        small_font = create_font(18)
        ui_font = create_font(34)
        message_font = create_font(28)
        special_font = create_font(16)
        instructions_headline_font = create_font(26)
        instructions_text_font = create_font(21)

        # Renderers
        digit_display = DigitRenderer()
        lives_display = LivesRenderer()

        # UI Components
        score_display = ScoreDisplay(layout, digit_display, x=70, width=6)
        lives_display_component = LivesDisplayComponent(
            layout, lives_display, x=365, max_lives=3
        )
        level_display_component = LevelDisplay(layout, digit_display, x=510)
        timer_display_component = TimerDisplay(layout, renderer, ui_font)
        message_display = MessageDisplay(layout, renderer, message_font)
        special_display = SpecialDisplay(layout, renderer, special_font)

        # Top and Bottom Bars
        top_bar_view = TopBarView(
            score_display,
            lives_display_component,
            level_display_component,
            timer_display_component,
            message_display,
            special_display,
        )
        bottom_bar_view = BottomBarView(
            message_display,
            special_display,
            timer_display_component,
        )

        # Views
        game_view = GameView(layout, block_manager, paddle, balls, renderer)
        if instructions_view is None:
            instructions_view = InstructionsView(
                layout,
                renderer,
                font,
                instructions_headline_font,
                instructions_text_font,
            )
        game_over_view = GameOverView(
            layout,
            renderer,
            font,
            small_font,
            lambda: game_state.score,
            reset_game_callback=None,  # To be set in main.py after instantiation
        )
        level_complete_view = LevelCompleteView(
            layout,
            renderer,
            font,
            small_font,
            game_state,
            level_manager,
            on_advance_callback=None,  # To be set in main.py after instantiation
        )

        return {
            "views": {
                "game": game_view,
                "instructions": instructions_view,
                "game_over": game_over_view,
                "level_complete": level_complete_view,
            },
            "top_bar": top_bar_view,
            "bottom_bar": bottom_bar_view,
            "game_over_view": game_over_view,
            "level_complete_view": level_complete_view,
            "game_view": game_view,
            "instructions_view": instructions_view,
            # Optionally return other UI components if needed
        }
