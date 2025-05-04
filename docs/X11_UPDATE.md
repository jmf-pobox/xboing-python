# X11 Dependency Analysis for XBoing

This document provides a comprehensive analysis of X11 dependencies in the XBoing codebase to inform migration planning from X11 to Wayland.

## 1. X11 Dependencies Overview

XBoing is deeply integrated with X11 libraries and makes extensive use of low-level X11 APIs. The code uses direct Xlib calls without any intermediate toolkit layer (like Motif, Xt, GTK, etc.), making it a "pure Xlib" application.

### 1.1 Key X11 Headers Used

The following X11 headers are included throughout the codebase:

- `X11/Xlib.h` - Core X11 library functions
- `X11/Xutil.h` - X11 utility functions
- `X11/Xos.h` - OS compatibility layer
- `X11/keysym.h` - Keyboard key symbol definitions  
- `X11/cursorfont.h` - Cursor definitions
- `xpm.h` (or `X11/xpm.h`) - XPM image format support

These headers are present in nearly all source files (26 .c files) and header files (25 .h files).

### 1.2 External Library Dependencies

Besides the core X11 libraries, XBoing has the following external dependencies:

- **XPM library**: Used extensively for loading and manipulating graphical assets
- **ALSA**: Recently added audio support (as indicated in the header comments in audio.h)

### 1.3 X11 API Usage

The codebase uses X11 APIs for multiple core functions:

1. **Graphics primitives**: Drawing lines, text, and shapes
2. **Image handling**: Loading XPM images and rendering to the screen
3. **Window management**: Creating, configuring, and managing windows
4. **Event handling**: Processing user input and window events
5. **Color management**: Allocating colors and managing colormaps
6. **Input handling**: Keyboard and mouse processing

## 2. Window Management Analysis

The window management in XBoing is implemented in several key files, with `stage.c` being the primary file for window creation and management.

### 2.1 Window Hierarchy

XBoing creates a hierarchy of X11 windows:

1. **mainWindow** - The top-level/parent window
2. **Multiple child windows**:
   - **playWindow** - The main game arena
   - **scoreWindow** - Displays the score
   - **levelWindow** - Shows level information
   - **messWindow** - Displays messages
   - **specialWindow** - For special effects/bonuses
   - **timeWindow** - Shows time information
   - **iconWindow** - Custom application icon
   - **bufferWindow** - Used for double-buffering (non-visible)
   - **blockWindow**, **typeWindow** - For the level editor
   - **inputWindow** - For user input/dialogs

### 2.2 Window Creation APIs

XBoing uses the following X11 window-related APIs:

- `XCreateSimpleWindow()` - Creates all game windows
- `XMapWindow()` - Makes windows visible
- `XSetWMProperties()` - Sets window manager properties
- `XSetWMNormalHints()` - Sets size hints for the window manager
- `XReconfigureWMWindow()` - Resizes windows
- `XChangeWindowAttributes()` - Configures window attributes
- `XSetWindowBackgroundPixmap()` - Sets window backgrounds
- `XIconifyWindow()` - Minimizes the window

### 2.3 Window Property Management

The game manages window properties through:

- Window size and position constraints (min/max sizes)
- Window manager hints for behavior
- Custom window icon creation
- Colormap installation and management

Notable in window management is the use of the `XpmCreatePixmapFromData()` function to create the window backgrounds and icon from embedded XPM data.

## 3. Event Handling Analysis

XBoing uses a traditional X11 event-driven architecture centered around an event loop that processes X11 events. The main event handling is implemented in `main.c` in the `handleEventLoop()` function.

### 3.1 Event Loop Structure

The event loop follows this general pattern:

1. Processes any pending X11 events with `XPending()` and `XNextEvent()`
2. Handles different event types through specific handler functions 
3. Updates game state and renders to the screen
4. Uses `XSync()` for display synchronization
5. Sleeps to control game speed with `sleepSync()`

### 3.2 Event Types Handled

XBoing processes these X11 event types:

- **KeyPress/KeyRelease**: Keyboard input via `XLookupString()` and key symbol mapping
- **ButtonPress/ButtonRelease**: Mouse button clicks
- **MotionNotify**: Mouse movement (used for paddle control)
- **Expose**: Window exposure events for redrawing content
- **MapNotify/UnmapNotify**: Window mapping state changes
- **StructureNotifyMask**: Window structure changes

### 3.3 Event Management

The code manages event flow through:

- `XSelectInput()` to set which events each window receives
- Event masks configured differently for each window based on its role
- Dynamic changes to event masks during gameplay to control input
- Manual event flushing with `XFlush()` to ensure all pending operations are processed

### 3.4 Input Focus Management

XBoing uses pointer grabbing for input control:
- `XGrabPointer()`/`XUngrabPointer()` to capture/release mouse input
- `XQueryPointer()` to get mouse position information
- Cursor management with `XDefineCursor()` and `XCreateFontCursor()`

## 4. Graphics and XPM Analysis

XBoing relies heavily on the XPM (X PixMap) library for all graphics assets, which is a key dependency for migrating to Wayland.

### 4.1 XPM Usage

The XPM library is used for:

1. **Loading graphics assets**: All game graphics (blocks, balls, backgrounds, etc.) are in XPM format
2. **Rendering game elements**: The rendering system is built around XPM pixel manipulation
3. **Animation**: The animation system relies on XPM pixmaps for sprite animation
4. **Window decorations**: Window backgrounds, icons, and UI elements

### 4.2 XPM APIs

Core XPM functions used throughout the codebase:

- `XpmCreatePixmapFromData()` - Creates pixmaps from embedded XPM data arrays
- `XpmFreeAttributes()` - Frees XPM attributes
- `XSetClipMask()`, `XSetClipOrigin()` - Used for XPM transparency
- `XCopyArea()` - Copies pixmap areas to windows or other pixmaps

### 4.3 Graphics Rendering Approach

XBoing's rendering system:

1. Uses the X11 graphics context system extensively:
   - Multiple GCs for different operations (copy, xor, and, or)
   - GC attribute manipulation for drawing operations
   
2. Uses a custom rendering pipeline:
   - `RenderShape()` function in `misc.c` handles shaped image rendering
   - Custom clipping and masking for transparencies
   - Window-based rendering with direct pixmap operations

3. Animation techniques:
   - Pixmap swapping for sprite animation
   - Direct-to-window rendering without an intermediate buffer in most cases
   - Simple double-buffering for some effects

## 5. Migration Strategy for Wayland

Based on the comprehensive analysis of XBoing's X11 dependencies, migrating to Wayland will require significant architectural changes. This section outlines a strategic approach for this migration.

### 5.1 Migration Challenges

1. **Direct X11 Dependencies**:
   - XBoing uses low-level Xlib functions extensively with no abstraction layer
   - The game relies on X11-specific concepts (pixmaps, graphics contexts, etc.)
   - XBoing depends on XPM for all graphics which is X11-specific

2. **Wayland Architecture Differences**:
   - Wayland lacks direct equivalents for many X11 concepts
   - No direct pixmap manipulation in Wayland
   - Different event handling model
   - No global pointer/keyboard grabbing

3. **Technical Debt**:
   - Legacy C code with limited modularity
   - Intermingling of UI and game logic
   - Limited separation of concerns

### 5.2 Recommended Approach

Given the extensive X11 dependencies, we recommend a **staged rewrite** rather than a direct port. This approach will involve:

1. **Create a Modern Graphics Abstraction Layer**:
   - Implement a rendering abstraction that can work with both X11 and Wayland
   - Replace direct Xlib calls with calls to this abstraction layer
   - Consider using an existing library like SDL2, which supports both X11 and Wayland backends

2. **Asset Modernization**:
   - Convert all XPM graphics to a more portable format (PNG or SVG)
   - Create a asset loading system independent of X11
   - Replace embedded XPM data with external resources

3. **Window Management Abstraction**:
   - Create a window management abstraction layer
   - Implement X11 and Wayland backends for this layer
   - Replace direct X11 window management with this abstraction

4. **Input Handling Refactoring**:
   - Redesign the input system to use an abstraction compatible with both X11 and Wayland
   - Remove direct keyboard and pointer grabbing
   - Implement more modern input handling patterns

### 5.3 Specific Technical Recommendations

1. **SDL2 as the Foundation**:
   - SDL2 provides cross-platform graphics, input, and window management
   - It supports both X11 and Wayland backends
   - Provides modern equivalents for most X11 functionality used by XBoing

2. **Rendering System Modernization**:
   - Replace direct X11 drawing with SDL2's 2D rendering API
   - Use hardware acceleration where available
   - Implement a proper sprite/animation system

3. **Architecture Improvements**:
   - Separate UI logic from game logic
   - Implement a proper game loop pattern
   - Create clean abstractions for key game components

4. **Audio System Update**:
   - Replace the custom ALSA audio system with SDL2's audio API
   - Create a unified sound system abstraction

### 5.4 Migration Process

1. **Initial Assessment and Planning** (Current Phase)
   - Analyze X11 dependencies (completed)
   - Define architectural boundaries
   - Create technical specifications for new components

2. **Prototype Phase**
   - Create a minimal SDL2-based prototype with core game mechanics
   - Test Wayland compatibility early
   - Benchmark performance against X11 version

3. **Incremental Implementation**
   - Build core engine components with SDL2
   - Reimplement game logic on top of new abstractions
   - Port game assets to modern formats

4. **Dual-Backend Support (Optional)**
   - Support both X11 and Wayland backends during transition
   - Allow runtime selection of display server

5. **Testing and Refinement**
   - Ensure consistent behavior across display servers
   - Optimize performance for both X11 and Wayland
   - Fix compatibility issues

By following this approach, XBoing can be modernized to work with Wayland while potentially improving its architecture, performance, and maintainability.

## 6. Conclusion

The XBoing codebase is deeply intertwined with X11/Xlib APIs and concepts, making a direct port to Wayland impractical. Instead, a staged rewrite using a cross-platform abstraction layer like SDL2 is recommended. This approach will not only enable Wayland support but also modernize the codebase and improve maintainability.

### 6.1 Summary of Key Findings

1. XBoing makes extensive use of low-level X11 APIs for:
   - Window management with multiple windows in a hierarchy
   - Graphics rendering with custom transparency handling
   - Input handling with keyboard and pointer grabbing
   - Event processing with a traditional X11 event loop

2. The graphics system is completely dependent on:
   - X11 pixmaps and graphic contexts
   - The XPM library for image loading and manipulation
   - Direct window drawing without modern buffering techniques

3. The codebase architecture:
   - Intermingles UI and game logic
   - Uses global state extensively
   - Lacks abstraction layers between game logic and display system

### 6.2 Next Steps

1. Prototype a minimal SDL2-based version that implements core game mechanics
2. Define a clear migration roadmap with specific milestones
3. Begin asset conversion from XPM to modern formats
4. Design abstraction layers for each major system (graphics, input, window management)
5. Gradually implement and test the new systems

Moving to Wayland presents an excellent opportunity to modernize XBoing while preserving its classic gameplay and charm. The resulting codebase will be more maintainable, portable, and future-proof.
