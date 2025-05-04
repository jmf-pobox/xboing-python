#!/usr/bin/env python3
"""
Simple test for pygame display
"""


import pygame


def main():
    """Simple pygame display test"""
    print("Starting pygame display test")

    # Initialize pygame
    print("Initializing pygame...")
    pygame.init()
    print("Pygame initialized")

    # Create a window
    print("Creating window...")
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Test Window")
    print("Window created")

    # Main loop
    print("Entering main loop")
    clock = pygame.time.Clock()
    running = True

    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear screen
        screen.fill((40, 44, 52))

        # Draw something
        pygame.draw.circle(screen, (255, 255, 255), (width // 2, height // 2), 50)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    # Clean up
    pygame.quit()
    print("Test complete")


if __name__ == "__main__":
    main()
