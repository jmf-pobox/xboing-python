# XBoing Level Implementation Plan

This document outlines the plan for implementing level support in the Python port of XBoing, using the original game's level data files.

## Original Level File Format

The original XBoing game uses a simple ASCII text format for level files:

1. **First line**: Level title (e.g., "Genesis")
2. **Second line**: Time bonus in seconds (e.g., 120)
3. **Remaining lines**: Grid representation of blocks (9 columns × 15 rows)

Example level file:
```
Genesis
120
.........
.........
rrrrrrrrr
bbbbbbbbb
ggggggggg
ttttttttt
.........
.........
000000000
yyyyyyyyy
ppppppppp
B...B...B
.........
.........
.........
```

## Block Types

Each character in the level grid represents a specific block type:

| Character | Block Type | Description |
|-----------|------------|-------------|
| `.` | NONE | Empty space |
| `r` | RED_BLK | Red block |
| `g` | GREEN_BLK | Green block |
| `b` | BLUE_BLK | Blue block |
| `t` | TAN_BLK | Tan block |
| `y` | YELLOW_BLK | Yellow block |
| `p` | PURPLE_BLK | Purple block |
| `w` | BLACK_BLK | Solid wall block |
| `X` | BOMB_BLK | Bomb block |
| `0`-`5` | COUNTER_BLK | Counter block (with hit points) |
| `B` | BULLET_BLK | Bullet (ammo) block |
| `c` | MAXAMMO_BLK | Maximum ammo block |
| `H` | HYPERSPACE_BLK | Hyperspace block |
| `D` | DEATH_BLK | Death block |
| `L` | EXTRABALL_BLK | Extra ball block |
| `M` | MGUN_BLK | Machine gun block |
| `W` | WALLOFF_BLK | Wall off block |
| `?` | RANDOM_BLK | Random changing block |
| `d` | DROP_BLK | Dropping block |
| `T` | TIMER_BLK | Extra time block |
| `m` | MULTIBALL_BLK | Multiple ball block |
| `s` | STICKY_BLK | Sticky block |
| `R` | REVERSE_BLK | Reverse paddle control block |
| `<` | PAD_SHRINK_BLK | Shrink paddle block |
| `>` | PAD_EXPAND_BLK | Expand paddle block |
| `+` | ROAMER_BLK | Roamer block |

## Implementation Tasks

### 1. Level Manager Class

Create a `LevelManager` class that will handle:

- Loading level files from the original game
- Parsing level data (title, time bonus, block layout)
- Creating block objects based on the level data
- Managing level progression
- Tracking remaining blocks
- Handling level completion

```python
class LevelManager:
    def __init__(self, levels_dir="../levels"):
        self.levels_dir = levels_dir
        self.current_level = 1
        self.max_levels = 80  # Original game has 80 levels
        self.level_title = ""
        self.time_bonus = 0
        self.blocks = []
        
    def load_level(self, level_num):
        # Load and parse level file
        # Create blocks based on level data
        
    def get_next_level(self):
        # Move to next level (with wraparound)
        
    def is_level_complete(self):
        # Check if all breakable blocks are destroyed
        
    def update(self, delta_time):
        # Update level timer and any animated blocks
```

### 2. Level Parser

Implement a level parser that can read the original level files:

```python
def parse_level_file(file_path):
    """Parse an XBoing level file and return level data."""
    with open(file_path, 'r') as f:
        # Read title (first line)
        title = f.readline().strip()
        
        # Read time bonus (second line)
        try:
            time_bonus = int(f.readline().strip())
        except ValueError:
            time_bonus = 120  # Default if parsing fails
            
        # Read block layout (remaining lines)
        block_layout = []
        for line in f:
            block_row = line.strip()
            if block_row:  # Skip empty lines
                block_layout.append(block_row)
                
    return {
        'title': title,
        'time_bonus': time_bonus,
        'layout': block_layout
    }
```

### 3. Block Factory

Create a block factory to instantiate the appropriate block type based on the character in the level file:

```python
class BlockFactory:
    @staticmethod
    def create_block(block_char, x, y):
        """Create a block based on character code from level file."""
        if block_char == '.':
            return None  # Empty space
        
        # Map character to block type
        block_type = {
            'r': SpriteBlock.TYPE_RED,
            'g': SpriteBlock.TYPE_GREEN,
            'b': SpriteBlock.TYPE_BLUE,
            't': SpriteBlock.TYPE_TAN,
            'y': SpriteBlock.TYPE_YELLOW,
            'p': SpriteBlock.TYPE_PURPLE,
            'w': SpriteBlock.TYPE_BLACK,
            # ... other block types
        }.get(block_char, SpriteBlock.TYPE_BLUE)  # Default to blue if unknown
        
        # Create and return the appropriate block
        return SpriteBlock(x, y, block_type)
```

### 4. Level Timer

Implement a timer system for the level bonus:

```python
class LevelTimer:
    def __init__(self, initial_seconds):
        self.time_remaining = initial_seconds
        self.is_active = True
        
    def update(self, delta_time):
        if self.is_active and self.time_remaining > 0:
            self.time_remaining -= delta_time
            
    def add_time(self, seconds):
        self.time_remaining += seconds
        
    def get_time_remaining(self):
        return max(0, int(self.time_remaining))
```

### 5. Level Display

Create UI elements to display level information:

- Level title
- Current level number
- Time remaining
- Score multiplier (based on remaining time)

### 6. File Path Management

Implement robust path handling to find level files:

```python
def get_level_file_path(level_num, levels_dir="../levels"):
    """Get the file path for a specific level number."""
    # Format level number with leading zeros
    level_name = f"level{level_num:02d}.data"
    return os.path.join(levels_dir, level_name)
```

### 7. Level Completion Logic

Implement logic to detect when a level is complete:

```python
def check_level_completion(blocks):
    """Check if all breakable blocks have been destroyed."""
    for block in blocks:
        if block.is_breakable and not block.is_destroyed:
            return False
    return True
```

### 8. Level Transition Effects

Add visual and audio effects for level transitions:

- Applause sound when level is complete
- Visual transition between levels
- Display of level title at start

### 9. Special Block Effects

Implement the special effects associated with different block types:

- Counter blocks that take multiple hits
- Bomb blocks that explode neighboring blocks
- Power-up blocks that give special abilities
- Animation for block destruction

### 10. Game Save/Load Support

Add the ability to save and load game progress:

- Save current level, score, and remaining blocks
- Load a previously saved game state
- Support for the original game's save file format if possible

## Milestone Plan

1. **Basic Level Loading**
   - Parse level files
   - Create basic blocks based on level data
   - Display static level layout

2. **Level Mechanics**
   - Implement level timer
   - Add level completion detection
   - Create level transitions

3. **Block Special Effects**
   - Implement the various block types
   - Add block animations
   - Create power-up effects

4. **Game Progression**
   - Track game progress through levels
   - Implement score multipliers based on time
   - Add level selection capability

5. **Polishing**
   - Add visual effects
   - Implement sound effects
   - Fine-tune level loading and display

## Integration Plan

1. Modify the main game loop to use the LevelManager
2. Update the collision system to work with the level-based blocks
3. Connect the UI to display level information
4. Link block destruction to score calculation
5. Add level progression when all blocks are destroyed

## Testing Strategy

1. Create test cases for each level file format
2. Verify that levels load correctly
3. Test special block behaviors
4. Confirm level progression works as expected
5. Compare with original game to ensure accuracy

## Resources Needed

1. Original level files from the XBoing game
2. Documentation of block types and their effects
3. Reference screenshots of original game levels
4. Audio files for level-related sounds