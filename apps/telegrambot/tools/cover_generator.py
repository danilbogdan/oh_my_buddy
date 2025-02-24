import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# Image and font parameters
WIDTH, HEIGHT = 1080, 1350  # Image size for Instagram
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/myfont.otf")  # Path to the font
BOLD_FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/myfont-bold.otf")  # Path to the bold font
ITALIC_FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/myfont-italic.otf")  # Path to the italic font
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

# Cover specific constants
COVER_COLORS = {
    "primary": "#0f3f41",  # Main background
    "accent": "#f0ac31",  # Bottom left
    "dark": "#151419",  # Top right
}
SHAPE_COUNT = 2  # Number of random shapes to generate
TITLE_FONT_SIZE = FONT_SIZE * 1.5
SUMMARY_FONT_SIZE = FONT_SIZE
STICKER_SIZE = 800  # Size for sticker image


def draw_diagonal_sections(draw, width, height):
    """Draw three-part diagonal sections of the cover"""
    # Draw accent section (bottom left)
    draw.polygon([(0, height), (width * 0.45, height), (0, height * 0.45)], fill=COVER_COLORS["accent"])

    # Draw dark section (top right)
    draw.polygon([(width, 0), (width, height * 0.55), (width * 0.55, 0)], fill=COVER_COLORS["dark"])


def wrap_text_for_cover(text, font, max_width, draw):
    """Wrap text to fit within specified width"""
    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def create_cover(title, summary, sticker_path=None, output_folder="output", return_buffer=False):
    """
    Generate a cover image with title, summary, and optional sticker
    """
    # Create base image with primary color
    img = Image.new("RGB", (WIDTH, HEIGHT), color=COVER_COLORS["primary"])
    draw = ImageDraw.Draw(img)

    # Draw the diagonal sections
    draw_diagonal_sections(draw, WIDTH, HEIGHT)

    # Load fonts
    title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
    summary_font = ImageFont.truetype(FONT_PATH, SUMMARY_FONT_SIZE)
    username_font = ImageFont.truetype(FONT_PATH, SUMMARY_FONT_SIZE // 2)

    # Calculate available width for text
    available_width = WIDTH - (2 * MARGIN_X)

    # Wrap and draw title
    title_lines = wrap_text_for_cover(title, title_font, available_width, draw)
    title_y = HEIGHT // 4
    line_height = int(TITLE_FONT_SIZE * 1.2)  # 20% spacing between lines

    for line in title_lines:
        draw.text((MARGIN_X, title_y), line, fill=TEXT_COLOR, font=title_font)
        title_y += line_height

    # Wrap summary text first to calculate total height
    summary_lines = wrap_text_for_cover(summary, summary_font, available_width, draw)
    summary_line_height = int(SUMMARY_FONT_SIZE * 1.2)  # 20% spacing between lines
    total_summary_height = (len(summary_lines) - 0.5) * summary_line_height  # Reduce height by half a line

    # Draw vertical line before summary
    summary_y = HEIGHT // 2
    line_x = MARGIN_X
    draw.line(
        [(line_x, summary_y), (line_x, summary_y + total_summary_height)],  # Adjust end point
        fill=TEXT_COLOR,
        width=1,
    )

    # Draw summary text
    for line in summary_lines:
        draw.text((MARGIN_X + 20, summary_y), line, fill=TEXT_COLOR, font=summary_font)
        summary_y += summary_line_height

    # Draw username and line
    username_text = USERNAME
    bbox = draw.textbbox((0, 0), username_text, font=username_font)
    username_text_width = bbox[2] - bbox[0]
    username_text_height = bbox[3] - bbox[1]
    username_x = WIDTH - MARGIN_X - username_text_width
    username_y = MARGIN_Y
    draw.text((username_x, username_y), username_text, fill=TEXT_COLOR, font=username_font)

    line_y = username_y + username_text_height // 2
    draw.line([(MARGIN_X, line_y), (username_x - 10, line_y)], fill=TEXT_COLOR, width=1)

    # Add sticker if provided
    if sticker_path and os.path.exists(sticker_path):
        try:
            sticker = Image.open(sticker_path)
            # Resize sticker maintaining aspect ratio
            sticker.thumbnail((STICKER_SIZE, STICKER_SIZE))
            # Place sticker in bottom right corner
            sticker_x = WIDTH - MARGIN_X - 400
            sticker_y = HEIGHT - MARGIN_Y - 400
            img.paste(sticker, (sticker_x, sticker_y), sticker if sticker.mode == "RGBA" else None)
        except Exception as e:
            print(f"Error adding sticker: {e}")

    if return_buffer:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered

    os.makedirs(output_folder, exist_ok=True)
    image_path = os.path.join(output_folder, "cover.png")
    img.save(image_path)
    return image_path


if __name__ == "__main__":
    create_cover(
        title="Кодить самому или использовать готовые решения: что выгоднее?",
        summary="Ты точно хочешь переплачивать за то, что можешь сделать сам?",
        # sticker_path="sticker3.webp",
    )
