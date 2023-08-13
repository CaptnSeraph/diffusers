from typing import List, Optional

import PIL.Image
import PIL.ImageOps
from packaging import version
from PIL import Image, ImageDraw, ImageFont

if version.parse(version.parse(PIL.__version__).base_version) >= version.parse("9.1.0"):
    PIL_INTERPOLATION = {
        "linear": PIL.Image.Resampling.BILINEAR,
        "bilinear": PIL.Image.Resampling.BILINEAR,
        "bicubic": PIL.Image.Resampling.BICUBIC,
        "lanczos": PIL.Image.Resampling.LANCZOS,
        "nearest": PIL.Image.Resampling.NEAREST,
    }
else:
    PIL_INTERPOLATION = {
        "linear": PIL.Image.LINEAR,
        "bilinear": PIL.Image.BILINEAR,
        "bicubic": PIL.Image.BICUBIC,
        "lanczos": PIL.Image.LANCZOS,
        "nearest": PIL.Image.NEAREST,
    }


def pt_to_pil(images):
    """
    Convert a torch image to a PIL image.
    """
    images = (images / 2 + 0.5).clamp(0, 1)
    images = images.cpu().permute(0, 2, 3, 1).float().numpy()
    images = numpy_to_pil(images)
    return images


def numpy_to_pil(images):
    """
    Convert a numpy image or a batch of images to a PIL image.
    """
    if images.ndim == 3:
        images = images[None, ...]
    images = (images * 255).round().astype("uint8")
    if images.shape[-1] == 1:
        # special case for grayscale (single channel) images
        pil_images = [Image.fromarray(image.squeeze(), mode="L") for image in images]
    else:
        pil_images = [Image.fromarray(image) for image in images]

    return pil_images

from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

# Create a function to wrap text
def wrap_text(text, draw, font, max_width):
    # Create a list to hold the lines of text
    lines = []
    # Split the text into individual words
    words = text.split()
    # Loop until there are no more words to process
    while words:
        # Create a variable to hold the text line
        line = ''
        # Try to get the width of the text line plus the next word
        try:
            # Attempt to use newer Pillow method
            text_width = font.getlength(line + words[0])
        except AttributeError:
            # Use older method for older versions of Pillow
            text_width = draw.textlength(line + words[0], font=font)
        # Check if the line is wider than the max width
        if text_width > max_width:
            # If the line is wider than the max width, add the word to the list
            lines.append(words.pop(0))
        else:
            # If the line is not wider than the max width, keep adding words until the line is too wide
            while words:
                # Add the next word to the line
                line += (words.pop(0) + ' ')
                try:
                    # Attempt to use newer Pillow method
                    text_width = font.getlength(line + words[0])
                except AttributeError:
                    # Use older method for older versions of Pillow
                    text_width = draw.textlength(line + words[0], font=font)
                # Check if the line is wider than the max width
                if text_width > max_width:
                    # If the line is wider than the max width, stop adding words
                    break
            # Add the line to the list
            lines.append(line)
    # Return the list of lines
    return lines


def make_image_grid(images: List[Image.Image], x_labels: List[str], y_labels: List[str], resize: Optional[int] = None) -> Image.Image:
    num_images = len(images)
    cols = len(x_labels)
    rows = len(y_labels)
    assert num_images == rows * cols, "Mismatch between number of images and grid dimensions."
    
    if resize is not None:
        images = [img.resize((resize, resize)) for img in images]

    w, h = images[0].size
    label_height = 100
    y_label_width = 300  # Reserved space for y-labels
    label_font = ImageFont.truetype("arial.ttf", 150)

    grid = Image.new("RGB", size=(cols * w + y_label_width, rows * (h + label_height)), color="white")
    draw = ImageDraw.Draw(grid)

    for i, img in enumerate(images):
        x_offset = i % cols * w + y_label_width  # Adjusted for y-label width
        y_offset = (i // cols) * (h + label_height)
        
        # Place image on grid
        grid.paste(img, box=(x_offset, y_offset + label_height))

        # Draw X and Y labels
        if i < cols:
            draw.text((x_offset + w//2 - 10*len(x_labels[i])//2, y_offset), x_labels[i], fill="black", font=label_font)
        
        if i % cols == 0:
            wrapped_text = wrap_text(y_labels[i // cols], draw, label_font, y_label_width)
            _, text_height = draw.textsize('A', font=label_font)
            total_text_height = len(wrapped_text) * text_height
                    # Approximate total height of text
            start_y = y_offset + label_height + h//2 - total_text_height // 2  # Centering the starting position of wrapped text
            for line in wrapped_text:
                text_width = draw.textlength(line, font=label_font)
                text_x = (y_label_width - text_width) // 2
                draw.text((text_x, start_y), line, fill="black", font=label_font)
                start_y += label_font.getsize('A')[1]


    return grid


def make_image_grid(images: List[Image.Image], x_labels: List[str], y_labels: List[str], resize: Optional[int] = None) -> Image.Image:
    num_images = len(images)
    cols = len(x_labels)
    rows = len(y_labels)
    assert num_images == rows * cols, "Mismatch between number of images and grid dimensions."
    
    if resize is not None:
        images = [img.resize((resize, resize)) for img in images]

    w, h = images[0].size
    label_height = 100
    y_label_width = 300  # Reserved space for y-labels
    label_font = ImageFont.truetype("arial.ttf", 150)

    grid = Image.new("RGB", size=(cols * w + y_label_width, rows * (h + label_height)), color="white")
    draw = ImageDraw.Draw(grid)

    for i, img in enumerate(images):
        x_offset = i % cols * w + y_label_width  # Adjusted for y-label width
        y_offset = (i // cols) * (h + label_height)
        
        # Place image on grid
        grid.paste(img, box=(x_offset, y_offset + label_height))

        # Draw X and Y labels
        if i < cols:
            text_width = draw.textlength(x_labels[i], font=label_font)
            draw.text((x_offset + w//2 - text_width//2, y_offset), x_labels[i], fill="black", font=label_font)
        
        if i % cols == 0:
            wrapped_text = wrap_text(y_labels[i // cols], draw, label_font, y_label_width)
            for line in wrapped_text:
                text_width = draw.textlength(line, font=label_font)
                text_x = (y_label_width - text_width) // 2
                draw.text((text_x, y_offset + label_height//2 - label_font.size//2), line, fill="black", font=label_font)
                y_offset += label_font.size

    return grid

