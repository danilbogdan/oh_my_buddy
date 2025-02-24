# Instagram Carousel Generator

A Python tool that generates Instagram-friendly carousel images from text input. The tool automatically splits long text into multiple images while maintaining readability and aesthetic consistency.

## Features

- Converts text into multiple 1080x1080 Instagram-friendly images
- Automatic text wrapping and pagination
- Consistent formatting with customizable margins
- Page numbering and username watermark
- Clean, readable output with customizable font settings

## Requirements

- Python 3.6+
- Pillow (PIL) library
- DejaVu Sans Bold font (included)

## Installation

1. Install the required Python package:
```bash
pip install Pillow
```

2. Ensure the DejaVu-Sans-Bold.ttf font file is in the same directory as the script.

## Usage

1. Create a text file (e.g., `post.txt`) with your content.

2. Run the script:
```bash
python carousel_generator.py
```

The script will read from `post.txt` and generate numbered images in the `output` directory.

## Customization

You can modify these variables in the script:
- `WIDTH, HEIGHT`: Image dimensions (default: 1080x1080)
- `FONT_SIZE`: Text size (default: 60)
- `MARGIN_X, MARGIN_Y`: Image margins (default: 100 pixels)
- `USERNAME`: Your Instagram handle
- `TEXT_COLOR`: Text color (default: "black")
- `BG_COLOR`: Background color (default: "white")

## Output

Generated images will be saved as:
- `output/post_1.png`
- `output/post_2.png`
- etc.

Each image includes your username and page numbers (e.g., "1/3") in the bottom right corner.