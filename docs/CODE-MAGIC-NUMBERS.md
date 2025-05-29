# Magic Numbers Documentation

This document lists all magic numbers found in the codebase, their location, and their purpose.
This information is intended to help improve code maintainability and readability.

## Format

Each entry follows this format:
- **Module**: Path to the file relative to src/
- **Line**: Line number where the magic number appears
- **Magic Number**: The actual numeric value
- **Purpose**: Explanation of what the number represents or does
- **Variable**: Name of the constant or variable that holds this value (if applicable)

## Magic Numbers List

### src/xboing/layout/game_layout.py

- **Module**: xboing/layout/game_layout.py
- **Line**: 161
- **Magic Number**: 495
- **Purpose**: Width of the play area in pixels
- **Variable**: play_width
- **Assessment**: Should be defined as a constant at the module level in xboing.py (it is already defined there as PLAY_WIDTH)
- **Status**: ⚠️ Still needs to be referenced from xboing.PLAY_WIDTH

- **Module**: xboing/layout/game_layout.py
- **Line**: 162
- **Magic Number**: 580
- **Purpose**: Height of the play area in pixels
- **Variable**: play_height
- **Assessment**: Should be defined as a constant at the module level in xboing.py (it is already defined there as PLAY_HEIGHT)
- **Status**: ⚠️ Still needs to be referenced from xboing.PLAY_HEIGHT

- **Module**: xboing/layout/game_layout.py
- **Line**: 163
- **Magic Number**: 70
- **Purpose**: Width of the side panels in pixels
- **Variable**: main_width
- **Assessment**: Should be defined as a constant at the module level in xboing.py (it is already defined there as MAIN_WIDTH)
- **Status**: ⚠️ Still needs to be referenced from xboing.MAIN_WIDTH

- **Module**: xboing/layout/game_layout.py
- **Line**: 164
- **Magic Number**: 130
- **Purpose**: Height of additional UI elements in pixels
- **Variable**: main_height
- **Assessment**: Should be defined as a constant at the module level in xboing.py (it is already defined there as MAIN_HEIGHT)
- **Status**: ⚠️ Still needs to be referenced from xboing.MAIN_HEIGHT

- **Module**: xboing/layout/game_layout.py
- **Line**: 175
- **Magic Number**: 224
- **Purpose**: Width of the score display area in pixels
- **Variable**: score_width
- **Assessment**: Should be in the ScoreDisplay class
- **Status**: ⚠️ Still needs to be moved to ScoreDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 176
- **Magic Number**: 30
- **Purpose**: Height of the message display area in pixels
- **Variable**: mess_height
- **Assessment**: Should be in the MessageDisplay class
- **Status**: ⚠️ Still needs to be moved to MessageDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 178
- **Magic Number**: 10, 42
- **Purpose**: Y position (10px from top) and height (42px) for score window
- **Variable**: Not yet named
- **Assessment**: Should be in the ScoreDisplay class
- **Status**: ⚠️ Still needs to be moved to ScoreDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 185-188
- **Magic Number**: 25, 5, 20, 52
- **Purpose**: Various positioning and sizing values for level window
- **Variable**: Not yet named
- **Assessment**: Should be in the LevelDisplay class
- **Status**: ⚠️ Still needs to be moved to LevelDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 195
- **Magic Number**: 60
- **Purpose**: Y position for play window (60px from top)
- **Variable**: Not yet named
- **Assessment**: Should be defined as a constant at the class level in GameLayout
- **Status**: ⚠️ Still needs to be defined as a constant

- **Module**: xboing/layout/game_layout.py
- **Line**: 202-205
- **Magic Number**: 35, 50, 10
- **Purpose**: Positioning values for message window
- **Variable**: Not yet named
- **Assessment**: Should be in the MessageDisplay class
- **Status**: ⚠️ Still needs to be moved to MessageDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 213-216
- **Magic Number**: 10, 65, 10, 180, 5
- **Purpose**: Positioning and sizing values for special window
- **Variable**: Not yet named
- **Assessment**: Should be in the SpecialDisplay class
- **Status**: ⚠️ Still needs to be moved to SpecialDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 224-227
- **Magic Number**: 5, 5, 8, 5
- **Purpose**: Positioning and sizing values for time window
- **Variable**: Not yet named
- **Assessment**: Should be in the TimerDisplay class
- **Status**: ⚠️ Still needs to be moved to TimerDisplay class

- **Module**: xboing/layout/game_layout.py
- **Line**: 290
- **Magic Number**: +2
- **Purpose**: Offset for background file naming convention
- **Variable**: Not yet named
- **Assessment**: Should be in the asset_paths.py or asset_loader.py module
- **Status**: ⚠️ Still needs to be moved to asset_paths.py or asset_loader.py
