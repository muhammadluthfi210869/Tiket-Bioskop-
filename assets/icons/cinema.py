from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_cinema_icon(size=512, output_path="cinema.png"):
    # Create a new image with black background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate positions
    padding = size * 0.1
    width = size - (2 * padding)
    height = width * 0.75  # 4:3 aspect ratio
    
    # Draw a gold colored cinema screen
    draw.rectangle(
        [(padding, padding), (padding + width, padding + height)],
        fill=(255, 215, 0),
        outline=(255, 215, 0),
        width=5
    )
    
    # Draw film strips at the bottom
    strip_height = size * 0.15
    strip_width = width
    strip_top = padding + height + (size * 0.05)
    
    draw.rectangle(
        [(padding, strip_top), (padding + strip_width, strip_top + strip_height)],
        fill=(20, 20, 20),
        outline=(255, 215, 0),
        width=3
    )
    
    # Draw film holes
    hole_size = strip_height * 0.4
    hole_padding = (strip_height - hole_size) / 2
    num_holes = 8
    hole_spacing = strip_width / (num_holes + 1)
    
    for i in range(1, num_holes + 1):
        hole_left = padding + (i * hole_spacing) - (hole_size / 2)
        hole_top = strip_top + hole_padding
        draw.ellipse(
            [(hole_left, hole_top), (hole_left + hole_size, hole_top + hole_size)],
            fill=(255, 215, 0)
        )
    
    # Save the icon
    img.save(output_path)
    print(f"Cinema icon saved to {output_path}")
    return output_path

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "cinema.png")
    create_cinema_icon(512, output_path) 