"""Generates a missing image for the bullet block in the game.

The image is generated by overlaying the bullet image 4 times on the yellow block image, centered at each position.
"""

import argparse

from PIL import Image


def generate_bullet_block(
    yellow_block_path: str, bullet_path: str, output_path: str
) -> None:
    """Generate a bullet block image by overlaying bullet.png 4 times on yellblk.png, centered at each position."""
    # Load base yellow block
    base = Image.open(yellow_block_path).convert("RGBA")
    # Load bullet image
    bullet = Image.open(bullet_path).convert("RGBA")
    bullet_w, bullet_h = bullet.size
    # Overlay bullets at the correct positions (centered)
    bullet_positions = [(6, 10), (15, 10), (24, 10), (33, 10)]
    for pos in bullet_positions:
        centered_pos = (pos[0] - bullet_w // 2, pos[1] - bullet_h // 2)
        base.alpha_composite(bullet, dest=centered_pos)
    # Save output
    base.save(output_path)
    print(f"Bullet block image saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate bullet block image for XBoing."
    )
    parser.add_argument(
        "--yellow-block", required=True, help="Path to yellblk.png (yellow block base)"
    )
    parser.add_argument(
        "--bullet", required=True, help="Path to bullet.png (bullet shape)"
    )
    parser.add_argument(
        "--output", default="bulletblock.png", help="Output path for generated image"
    )
    args = parser.parse_args()
    generate_bullet_block(args.yellow_block, args.bullet, args.output)
