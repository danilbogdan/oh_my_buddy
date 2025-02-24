import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Image and font parameters
WIDTH, HEIGHT = 1080, 1350  # Image size for Instagram
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/myfont.otf")  # Path to the font
FONT_SIZE = 36
TEXT_COLOR = "#eaeaea"
BG_COLOR = "#0f3f41"
USERNAME = "@progger_bob"
DIAMOND_COLOR = "#151419"
DIAMOND_SIZE = 1000
LINE_HEIGHT_SCALE = 2

# Aesthetic margins (padding)
MARGIN_X = 150  # Left and right margin
MARGIN_Y = 100  # Top and bottom margin

# Shape parameters


def draw_half_rhombus(draw, width, height, is_odd_page):
    """
    Draws half of a rhombus (diamond) on the side
    """
    center_y = 300 + height // 2
    if is_odd_page:
        # Right half of rhombus
        points = [
            (width, center_y - DIAMOND_SIZE // 2),
            (width - DIAMOND_SIZE // 2, center_y),
            (width, center_y + DIAMOND_SIZE // 2),
        ]
    else:
        # Left half of rhombus
        points = [
            (0, center_y - DIAMOND_SIZE // 2),
            (DIAMOND_SIZE // 2, center_y),
            (0, center_y + DIAMOND_SIZE // 2),
        ]

    draw.polygon(points, fill=DIAMOND_COLOR)


def wrap_text(text, font, max_width):
    """
    Splits text into lines so that each line does not exceed max_width (in pixels).
    Iterates through words and assembles a line, measuring its width using the font.
    """
    paragraphs = text.split("\n")
    lines = []
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)

    for paragraph in paragraphs:
        words = paragraph.split()
        current_line = ""
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
        lines.append("")  # Add an empty line to separate paragraphs

    if lines and lines[-1] == "":
        lines.pop()  # Remove the last empty line if it exists

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
    os.makedirs(output_folder, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Draw shapes based on page number
    is_odd_page = page_number % 2 == 1
    draw_half_rhombus(draw, WIDTH, HEIGHT, is_odd_page)

    if font is None:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    username_font = ImageFont.truetype(FONT_PATH, FONT_SIZE // 2)

    draw = ImageDraw.Draw(img)
    text_block_height = len(lines) * line_height
    y = (HEIGHT - text_block_height) // 2
    x = margin_x
    for line in lines:
        draw.text((x, y), line, fill=TEXT_COLOR, font=font, align="left")
        y += line_height

    # Draw username at the top right
    username_text = USERNAME
    bbox = draw.textbbox((0, 0), username_text, font=username_font)
    username_text_width = bbox[2] - bbox[0]
    username_text_height = bbox[3] - bbox[1]
    username_x = WIDTH - margin_x - username_text_width
    username_y = margin_y
    draw.text((username_x, username_y), username_text, fill=TEXT_COLOR, font=username_font)
    # Draw a line in the middle of the username height
    line_y = username_y + username_text_height // 2
    draw.line([(margin_x, line_y), (username_x - 10, line_y)], fill=TEXT_COLOR, width=1)

    page_number_text = f"{page_number}/{total_pages}"
    page_number_y = HEIGHT - margin_y - username_text_height
    draw.text((WIDTH - margin_x, page_number_y), page_number_text, fill=TEXT_COLOR, font=username_font)

    if return_buffer:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered

    image_path = os.path.join(output_folder, f"post_{page_number}.png")
    img.save(image_path)


def generate_carousel(text, output_folder="output", return_buffer=False, page_separator="---"):
    """
    Generates a carousel of images for Instagram:
    - First, the available area for text is calculated considering the margins.
    - Then the text is split into lines (using pixel width) with wrap_text.
    - The line height is determined (with a small line spacing).
    - Lines are grouped into pages based on a special page separator.
    - An image is created for each page.
    """
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    # Calculate the available area for text
    content_width = WIDTH - 2 * MARGIN_X
    content_height = HEIGHT - 2 * MARGIN_Y

    # Split text into pages based on the page separator
    pages_text = text.split(page_separator)

    # Create a temporary image to calculate line height
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), "Ay", font=font)
    base_line_height = bbox[3] - bbox[1]
    # Add line spacing (e.g., 20%)
    line_height = int(base_line_height * LINE_HEIGHT_SCALE)

    pages = []
    for page_text in pages_text:
        # Split page text into lines so they do not exceed content_width
        lines = wrap_text(page_text, font, content_width)

        # Check if the lines fit into one page, otherwise split into multiple pages
        current_page_lines = []
        current_page_height = 0
        for line in lines:
            if current_page_height + line_height > content_height:
                pages.append(current_page_lines)
                current_page_lines = []
                current_page_height = 0
            current_page_lines.append(line)
            current_page_height += line_height
        if current_page_lines:
            pages.append(current_page_lines)

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
