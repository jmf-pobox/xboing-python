#!/usr/bin/env python3
"""
Headless test for audio playback in XBoing
"""

import os
import pygame
import time
import sys

def main():
    """Test loading and playing WAV files without a display"""
    print("Initializing pygame for headless audio test")
    
    # Initialize pygame without display
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    
    # Initialize mixer specifically
    pygame.mixer.init()
    print("Pygame audio initialized")
    
    # Get the path to the sounds directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.join(base_dir, 'src', 'assets', 'sounds')
    
    print(f"Looking for sounds in: {sounds_dir}")
    
    # List of sound files to test
    sound_files = [
        'boing.wav',
        'click.wav',
        'bomb.wav',
        'applause.wav',
        'game_over.wav'
    ]
    
    # Try to load and play each sound
    for sound_file in sound_files:
        sound_path = os.path.join(sounds_dir, sound_file)
        print(f"Testing sound: {sound_path}")
        
        if os.path.exists(sound_path):
            print(f"File exists: {sound_path}")
            try:
                print(f"Loading sound...")
                sound = pygame.mixer.Sound(sound_path)
                print(f"Sound loaded, playing...")
                channel = sound.play()
                print(f"Played sound {sound_file}")
                
                # Wait until the sound has finished playing
                playing = True
                start_time = time.time()
                timeout = 2.0  # Maximum wait time in seconds
                
                while playing and (time.time() - start_time < timeout):
                    if channel is None or not channel.get_busy():
                        playing = False
                    time.sleep(0.1)
                    
                print(f"Sound finished playing: {sound_file}")
                
            except Exception as e:
                print(f"Error playing {sound_file}: {e}")
        else:
            print(f"File not found: {sound_path}")
    
    print("Test complete")
    pygame.quit()
    
if __name__ == "__main__":
    main()