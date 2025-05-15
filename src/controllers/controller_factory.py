from controllers.controller_manager import ControllerManager
from controllers.game_controller import GameController
from controllers.game_over_controller import GameOverController
from controllers.instructions_controller import InstructionsController
from controllers.level_complete_controller import LevelCompleteController
from ui.game_view import GameView


class ControllerFactory:
    """
    Factory for creating and registering all controllers for XBoing.
    
    This class centralizes controller instantiation and registration logic, keeping main.py clean and focused
    on high-level orchestration. All dependencies must be passed in; no direct imports
    of game state or event bus should occur here.
    
    The factory creates four main controllers:
    - GameController: Handles the main gameplay
    - InstructionsController: Manages the instructions screen
    - LevelCompleteController: Handles level completion logic and transitions
    - GameOverController: Manages game over state and UI
    """

    @staticmethod
    def create_and_register_controllers(
        game_state,
        level_manager,
        balls,
        paddle,
        block_manager,
        input_manager,
        layout,
        renderer,
        audio_manager,
        event_sound_map,
        ui_manager,
        quit_callback,
        reset_game_callback=None,
        instructions_controller=None,
    ):
        """
        Construct and register all controllers, returning the ControllerManager and controller references.
        
        This method instantiates all necessary game controllers, registers them with the controller manager,
        and sets the initial active controller to "game".
        
        Args:
            game_state: The current state of the game (score, lives, etc.)
            level_manager: Manager for loading and transitioning between levels
            balls: Collection of ball objects in the game
            paddle: The player's paddle object
            block_manager: Manager for blocks and their behaviors
            input_manager: Manager for handling user input
            layout: Layout information for the game screen
            renderer: Graphics rendering system
            audio_manager: Manager for audio playback and volume control
            event_sound_map: Mapping of game events to sound effects
            ui_manager: Manager for UI views and transitions
            quit_callback: Function to call when quitting the game
            reset_game_callback: Function to reset the game (used by game over controller)
            instructions_controller: Optional pre-configured instructions controller
            
        Returns:
            dict: A dictionary containing:
                - "controller_manager": The main controller manager
                - "game_controller": Reference to the main game controller
                - "instructions_controller": Reference to the instructions controller
                - "level_complete_controller": Reference to the level complete controller
                - "game_over_controller": Reference to the game over controller
        """
        controller_manager = ControllerManager()

        # Create the main game controller
        game_controller = GameController(
            game_state,
            level_manager,
            balls,
            paddle,
            block_manager,
            input_manager=input_manager,
            layout=layout,
            renderer=renderer,
            audio_manager=audio_manager,
            event_sound_map=event_sound_map,
            quit_callback=quit_callback,
            ui_manager=ui_manager,
        )
        
        # Create or use provided instructions controller
        if instructions_controller is None:
            instructions_controller = InstructionsController(
                on_exit_callback=lambda: ui_manager.set_view(ui_manager.previous_view or "game"),
                audio_manager=audio_manager,
                quit_callback=quit_callback,
                ui_manager=ui_manager,
            )
            
        # Create level complete controller
        level_complete_controller = LevelCompleteController(
            game_state,
            level_manager,
            balls,
            game_controller,
            ui_manager,
            (
                ui_manager.views["game"]
                if hasattr(ui_manager, "views") and "game" in ui_manager.views
                else None
            ),
            layout,
            on_advance_callback=None,  # To be set in main.py after instantiation
            audio_manager=audio_manager,
            quit_callback=quit_callback,
        )
        
        # Create game over controller
        game_over_controller = GameOverController(
            game_state=game_state,
            level_manager=level_manager,
            balls=balls,
            game_controller=game_controller,
            game_view=(
                ui_manager.views["game"]
                if hasattr(ui_manager, "views") and "game" in ui_manager.views
                else GameView(layout, block_manager, paddle, balls, renderer)
            ),
            layout=layout,
            ui_manager=ui_manager,
            audio_manager=audio_manager,
            quit_callback=quit_callback,
        )
        
        # Register all controllers with the controller manager
        controller_manager.register_controller("game", game_controller)
        controller_manager.register_controller("instructions", instructions_controller)
        controller_manager.register_controller(
            "level_complete", level_complete_controller
        )
        controller_manager.register_controller("game_over", game_over_controller)
        
        # Set the initial active controller
        controller_manager.set_controller("game")

        # Return dictionary of controllers and manager for use in main.py
        return {
            "controller_manager": controller_manager,
            "game_controller": game_controller,
            "instructions_controller": instructions_controller,
            "level_complete_controller": level_complete_controller,
            "game_over_controller": game_over_controller,
        }