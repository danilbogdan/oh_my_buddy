import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Image and font parameters
WIDTH, HEIGHT = 1080, 1080  # Image size for Instagram
FONT_PATH = os.path.join(os.path.dirname(__file__), "OpenSans-Light.ttf")  # Path to the font
FONT_SIZE = 60
TEXT_COLOR = "black"
BG_COLOR = "white"
USERNAME = "@progger_bob"

# Aesthetic margins (padding)
MARGIN_X = 100  # Left and right margin
MARGIN_Y = 100  # Top and bottom margin


def wrap_text(text, font, max_width):
    """
    Splits text into lines so that each line does not exceed max_width (in pixels).
    Iterates through words and assembles a line, measuring its width using the font.
    """
    words = text.split()
    lines = []
    current_line = ""
    # Create a temporary image to measure text
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    for word in words:
        test_line = word if not current_line else current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_image_with_lines(
    lines,
    page_number,
    total_pages,
    margin_x,
    margin_y,
    line_height,
    output_folder="output",
    font=None,
    return_buffer=False,
):
    """
    Creates an image page by drawing the given list of lines with left alignment.
    Also adds a signature with the username and page number in the bottom right corner.
    Optionally returns the image as a base64 encoded string.
    """
    os.makedirs(output_folder, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    if font is None:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    # Font for the signature (e.g., half the size of the main font)
    username_font = ImageFont.truetype(FONT_PATH, FONT_SIZE // 2)

    # Calculate the total height of the text block
    text_block_height = len(lines) * line_height

    # Calculate the starting y position to center the text block vertically
    y = (HEIGHT - text_block_height) // 2

    # Draw text starting from the calculated y position within the margins
    x = margin_x
    for line in lines:
        draw.text((x, y), line, fill=TEXT_COLOR, font=font, align="left")
        y += line_height

    # Form the signature in the bottom right corner within the margins
    username_text = f"{USERNAME} • {page_number}/{total_pages}"
    bbox = draw.textbbox((0, 0), username_text, font=username_font)
    username_text_width = bbox[2] - bbox[0]
    username_text_height = bbox[3] - bbox[1]
    username_x = WIDTH - margin_x - username_text_width
    username_y = HEIGHT - margin_y - username_text_height
    draw.text((username_x, username_y), username_text, fill=TEXT_COLOR, font=username_font)

    if return_buffer:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered

    # Save the image
    image_path = os.path.join(output_folder, f"post_{page_number}.png")
    img.save(image_path)


def generate_carousel(text, output_folder="output", return_buffer=False):
    """
    Generates a carousel of images for Instagram:
    - First, the available area for text is calculated considering the margins.
    - Then the text is split into lines (using pixel width) with wrap_text.
    - The line height is determined (with a small line spacing).
    - Lines are grouped into pages so that each page contains an equal number of lines.
    - An image is created for each page.
    """
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    # Calculate the available area for text
    content_width = WIDTH - 2 * MARGIN_X
    content_height = HEIGHT - 2 * MARGIN_Y

    # Split text into paragraphs based on newlines
    paragraphs = text.split("\n")

    # Create a temporary image to calculate line height
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), "Ay", font=font)
    base_line_height = bbox[3] - bbox[1]
    # Add line spacing (e.g., 20%)
    line_height = int(base_line_height * 1.2)

    # Determine how many lines fit on one page
    max_lines_per_page = content_height // line_height
    if max_lines_per_page < 1:
        max_lines_per_page = 1  # in case the margins are too large

    pages = []
    for paragraph in paragraphs:
        # Split paragraph into lines so they do not exceed content_width
        lines = wrap_text(paragraph, font, content_width)
        # Split the list of lines into groups (pages)
        paragraph_pages = [lines[i : i + max_lines_per_page] for i in range(0, len(lines), max_lines_per_page)]
        pages.extend(paragraph_pages)

    total_pages = len(pages)

    # Generate an image for each page
    images = []
    for i, page_lines in enumerate(pages):
        image = create_image_with_lines(
            lines=page_lines,
            page_number=i + 1,
            total_pages=total_pages,
            margin_x=MARGIN_X,
            margin_y=MARGIN_Y,
            line_height=line_height,
            output_folder=output_folder,
            font=font,
            return_buffer=return_buffer,
        )
        if image:
            images.append(image)
    return images


# Example usage
if __name__ == "__main__":
    with open("post.txt", "r", encoding="utf-8") as file:
        post_text = file.read()
    generate_carousel(post_text)
