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
    Splits text into lines and keeps track of character offsets for each line.
    Returns a list of tuples (line_text, start_offset).
    """
    paragraphs = text.split("\n")
    lines = []
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    current_offset = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        current_line = ""
        line_start_offset = current_offset

        for word in words:
            test_line = word if not current_line else current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append((current_line, line_start_offset))
                    current_offset = line_start_offset + len(current_line) + 1
                    line_start_offset = current_offset
                    current_line = word
                else:
                    current_line = word

        if current_line:
            lines.append((current_line, line_start_offset))
            current_offset = line_start_offset + len(current_line) + 1

        # Add offset for the newline character
        current_offset += 1

    return lines


def apply_entities(draw, text, font, entities, x, y, start_offset):
    """
    Draws text with specified entities, adjusting for line offsets.
    """
    current_pos = 0
    x_offset = 0
    text_length = len(text)

    # Filter and adjust entities for this line
    line_entities = []
    for entity in entities:
        entity_start = entity["offset"] - start_offset
        entity_end = entity_start + entity["length"]

        # Skip if entity is not in this line
        if entity_start >= text_length or entity_end <= 0:
            continue

        # Adjust entity boundaries to this line
        adjusted_entity = {
            "offset": max(0, entity_start),
            "length": min(text_length - max(0, entity_start), entity["length"] - max(0, -entity_start)),
            "type": entity["type"],
        }
        line_entities.append(adjusted_entity)

    sorted_entities = sorted(line_entities, key=lambda e: e["offset"])

    # Apply formatting with adjusted entities
    current_pos = 0
    for entity in sorted_entities:
        # Draw default text before entity
        if entity["offset"] > current_pos:
            default_text = text[current_pos : entity["offset"]]
            draw.text((x + x_offset, y), default_text, fill=TEXT_COLOR, font=font)
            bbox = draw.textbbox((0, 0), default_text, font=font)
            x_offset += bbox[2] - bbox[0]

        # Draw formatted text
        entity_text = text[entity["offset"] : entity["offset"] + entity["length"]]
        entity_font = font
        if entity["type"] == "bold":
            entity_font = ImageFont.truetype(BOLD_FONT_PATH, FONT_SIZE)
        elif entity["type"] == "italic":
            entity_font = ImageFont.truetype(ITALIC_FONT_PATH, FONT_SIZE)

        draw.text((x + x_offset, y), entity_text, fill=TEXT_COLOR, font=entity_font)
        bbox = draw.textbbox((0, 0), entity_text, font=entity_font)
        x_offset += bbox[2] - bbox[0]
        current_pos = entity["offset"] + entity["length"]

    # Draw remaining default text
    if current_pos < len(text):
        default_text = text[current_pos:]
        draw.text((x + x_offset, y), default_text, fill=TEXT_COLOR, font=font)


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
    entities=None,
    page_offset=0,
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

    # Adjust line offsets based on page offset
    for line_text, line_relative_offset in lines:
        absolute_offset = page_offset + line_relative_offset
        apply_entities(draw, line_text, font, entities, x, y, absolute_offset)
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


def generate_carousel(text, entities=None, output_folder="output", return_buffer=False, page_separator="---"):
    """
    Generates a carousel of images for Instagram with proper text offset tracking across pages.
    """
    if entities is None:
        entities = []
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    content_width = WIDTH - 2 * MARGIN_X
    content_height = HEIGHT - 2 * MARGIN_Y

    # Calculate line height first
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), "Ay", font=font)
    base_line_height = bbox[3] - bbox[1]
    line_height = int(base_line_height * LINE_HEIGHT_SCALE)

    # Track global text offset
    current_offset = 0
    pages_with_offsets = []

    # Split text into pages and track offsets
    pages_text = text.split(page_separator)
    for page_text in pages_text:
        page_start_offset = current_offset
        lines = wrap_text(page_text, font, content_width)

        # Check if lines fit into one page, otherwise split into multiple pages
        current_page_lines = []
        current_page_height = 0
        for line_text, line_offset in lines:
            if current_page_height + line_height > content_height and current_page_lines:
                pages_with_offsets.append((current_page_lines, page_start_offset))
                page_start_offset = page_start_offset + sum(len(text) + 1 for text, _ in current_page_lines)
                current_page_lines = []
                current_page_height = 0
            current_page_lines.append((line_text, line_offset))
            current_page_height += line_height

        if current_page_lines:
            pages_with_offsets.append((current_page_lines, page_start_offset))

        # Update global offset including the page separator
        current_offset += len(page_text) + len(page_separator)

    total_pages = len(pages_with_offsets)

    # Generate images with proper offset tracking
    images = []
    for i, (page_lines, page_offset) in enumerate(pages_with_offsets):
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
            entities=entities,
            page_offset=page_offset,  # Pass the page offset
        )
        if image:
            images.append(image)
    return images


# Example usage
if __name__ == "__main__":
    with open("post.txt", "r", encoding="utf-8") as file:
        post_text = file.read()
    generate_carousel(
        post_text,
        entities=[{"offset": 220, "length": 29, "type": "bold"}, {"offset": 100, "length": 29, "type": "italic"}],
    )
