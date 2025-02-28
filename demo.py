import os
import pandas as pd
import random
from PIL import Image, ImageDraw, ImageFont

# Load quotes from Excel file
file_path = "data/Motivational_Quotes.xlsx"
df = pd.read_excel(file_path)

# Ensure output folder exists
output_folder = "data/generated_images"
os.makedirs(output_folder, exist_ok=True)

# Define image size and font
img_width, img_height = 1080, 1080  # Square format for social media
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Default font

# Background colors
background_colors = ["#1E3A8A", "#065F46", "#B91C1C", "#78350F", "#4B5563"]  # Dark blue, green, red, brown, gray

# Generate images for quotes
image_paths = []
for index, row in df.iterrows():
    quote = row["Quote"]
    
    # Create image
    img = Image.new("RGB", (img_width, img_height), color=random.choice(background_colors))
    draw = ImageDraw.Draw(img)

    # Load font
    font = ImageFont.truetype(font_path, 50)

    # Split text into multiple lines for readability
    max_width = img_width - 100  # Leave margin
    words = quote.split(" ")
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_width, _ = draw.textsize(test_line, font=font)
        
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)  # Add the last line

    # Calculate text height
    text_height = len(lines) * 60  # Approximate line height
    y_text = (img_height - text_height) // 2  # Center text vertically

    # Draw text
    for line in lines:
        text_width, _ = draw.textsize(line, font=font)
        x_text = (img_width - text_width) // 2  # Center text horizontally
        draw.text((x_text, y_text), line, font=font, fill="white")
        y_text += 60  # Move to next line

    # Save image
    img_path = os.path.join(output_folder, f"quote_{index + 1}.png")
    img.save(img_path)
    image_paths.append(img_path)

# Return the list of generated images
image_paths[:10]  # Preview first 10 images paths
