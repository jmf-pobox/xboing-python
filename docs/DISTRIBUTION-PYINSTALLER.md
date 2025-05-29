# Building XBoing Executables with PyInstaller

This document explains how to build standalone executables for the XBoing game using PyInstaller.

## Prerequisites

- Python 3.10 or higher
- Hatch (for the recommended approach)

## Quick Start (Recommended)

The easiest way to build an executable is using the provided Hatch command:

```bash
# Create and activate the development environment if you haven't already
hatch env create
hatch shell

# Build the executable
hatch run build-exe
```

This will:
1. Install PyInstaller if it's not already installed
2. Create a spec file with the correct configuration
3. Build the executable
4. Place the executable in the `dist` directory

## Manual Approach

If you prefer to run the build script directly:

```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python -m xboing.scripts.build_executable
```

## Running the Executable

After building, you can find the executable in the `dist` directory:

- **Windows**: `dist\xboing.exe`
- **macOS**: `dist/xboing`
- **Linux**: `dist/xboing`

On macOS, you may need to allow the app in Security & Privacy settings.

## Customizing the Build

If you need to customize the build process, you can:

1. Run the build script once to generate the `xboing.spec` file
2. Edit the spec file to customize the build
3. Run PyInstaller directly with the spec file:

```bash
pyinstaller xboing.spec
```

## Troubleshooting

### Missing Assets

If the executable can't find assets:

1. Make sure the assets are included in the spec file
2. Check that the asset paths are correctly resolved in the code
3. Verify that the assets are correctly bundled in the executable

## Cross-Platform Building

PyInstaller builds executables for the platform it's running on. This means:

- **To build a Windows executable (.exe)**: You need to run PyInstaller on Windows
- **To build a macOS app**: You need to run PyInstaller on macOS
- **To build a Linux executable**: You need to run PyInstaller on Linux

There is no official cross-platform building support in PyInstaller. Each platform has specific requirements:

- **Windows executables** need Windows-specific libraries and COM objects
- **macOS apps** need specific bundle structures and macOS-specific libraries
- **Linux executables** need Linux-specific shared libraries

### Alternatives for Cross-Platform Building

If you need to build for multiple platforms without access to all platforms:

1. **Use CI/CD pipelines**: Set up GitHub Actions or other CI services to build on multiple platforms
2. **Use virtual machines**: Run Windows/Linux/macOS in VMs to build for each platform
3. **Use Docker**: For Linux builds from non-Linux platforms (limited to Linux targets)
4. **Use Wine**: For Windows builds from Linux (experimental, not officially supported)

### Platform-Specific Issues

#### Windows

- If you get "Access Denied" errors, try running as administrator
- For icon issues, make sure the icon file is a valid .ico file

#### macOS

- If you get "App is damaged" messages, try:
  ```bash
  xattr -cr dist/xboing
  ```
- For notarization, see the [PyInstaller macOS documentation](https://pyinstaller.org/en/stable/usage.html#macos)

#### Linux

- If you get missing library errors, you may need to install additional dependencies
- Consider using AppImage for better distribution

## How It Works

The build process:

1. Uses PyInstaller to analyze the application and its dependencies
2. Creates a spec file that includes all assets (images, sounds, levels, etc.)
3. Builds a standalone executable that includes Python and all dependencies
4. Packages everything into a single file or directory

At runtime, the executable:
1. Extracts the bundled files to a temporary directory
2. Sets up the Python environment
3. Runs the application

The application uses a special path resolution mechanism to find assets both during development and when running from the executable.
