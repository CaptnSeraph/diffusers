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

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        if font.getsize(line + words[0])[0] > max_width:
            # Handle case where single word is longer than max_width
            lines.append(words.pop(0))
        else:
            while words and font.getsize(line + words[0])[0] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)
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
            wrapped_text = wrap_text(y_labels[i // cols], label_font, y_label_width)
            total_text_height = len(wrapped_text) * label_font.getsize('A')[1]  # Approximate total height of text
            start_y = y_offset + label_height + h//2 - total_text_height // 2  # Centering the starting position of wrapped text
            for line in wrapped_text:
                text_width = draw.textlength(line, font=label_font)
                text_x = (y_label_width - text_width) // 2
                draw.text((text_x, start_y), line, fill="black", font=label_font)
                start_y += label_font.getsize('A')[1]


    return grid

