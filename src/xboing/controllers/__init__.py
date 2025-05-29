"""Controllers package for XBoing, containing all controller classes and logic.

This package implements the controller layer of the MVC architecture for XBoing.
It contains:

1. A base Controller protocol that defines the interface for all controllers
2. A ControllerManager that handles registration and switching between controllers
3. Specialized controllers for different game states and views:
   - GameController: Manages the main gameplay, including ball physics, paddle movement,
     collision detection, block interactions, and level progression
   - WindowController: Handles global/system events like volume control, mute toggling,
     quitting the game, and mouse visibility
   - InstructionsController: Manages the instructions view and its interactions
   - GameOverController: Handles the game over state and related user interactions
   - LevelCompleteController: Manages the level complete state and transitions

Controllers receive input events, update the game state, and trigger
appropriate actions based on the current game context.
"""
