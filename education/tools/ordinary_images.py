"""Encode ordinary reader illustrations at the owner-specified JPEG quality."""
from pathlib import Path
from PIL import Image


def jpeg85(source, destination):
    destination = Path(destination)
    if destination.suffix.lower() not in {'.jpg', '.jpeg'}:
        raise ValueError('JPEG output requires a .jpg or .jpeg extension')
    with Image.open(source) as image:
        image.convert('RGB').save(destination, 'JPEG', quality=85, optimize=True)
