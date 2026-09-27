from pathlib import Path

import pandas as pd
from PIL import Image, ImageOps, UnidentifiedImageError


def _normalize_image(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.width <= 0 or image.height <= 0:
        raise ValueError("image has invalid dimensions")
    return image.convert("RGB")


def load_image(path) -> Image.Image:
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"input image not found: {image_path}")
    try:
        with Image.open(image_path) as image:
            return _normalize_image(image).copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"could not decode image: {image_path}") from exc


def load_uploaded_image(uploaded_file) -> Image.Image:
    try:
        with Image.open(uploaded_file) as image:
            return _normalize_image(image).copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("the uploaded file is not a valid JPEG or PNG image") from exc


def dataframe_to_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")

