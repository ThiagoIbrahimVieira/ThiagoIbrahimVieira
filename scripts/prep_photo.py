"""
prep_photo.py — remove background, boost contrast, composite onto white.
Output: source-prepped.png next to the script.
"""
from pathlib import Path
import sys
import numpy as np
import cv2
from rembg import remove
from PIL import Image


def main(src: str) -> None:
    src_path = Path(src)
    if not src_path.exists():
        sys.exit(f"not found: {src}")

    raw = Image.open(src_path).convert("RGBA")
    # rembg -> transparent background
    cut = remove(np.asarray(raw))
    cut_img = Image.fromarray(cut).convert("RGBA")

    # Grayscale of the subject only (ignore alpha)
    gray = np.asarray(cut_img.convert("L"))

    # CLAHE — local contrast; 2.0 clip keeps skin realistic, not crunchy
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)

    # Composite onto pure white so background pixels map to "space" glyph
    alpha = cut_img.split()[3]
    white = np.full_like(eq, 255, dtype=np.uint8)
    a = np.asarray(alpha).astype(np.float32) / 255.0
    composed = (eq.astype(np.float32) * a + white.astype(np.float32) * (1 - a)).astype(np.uint8)

    out = Path(__file__).parent / "source-prepped.png"
    Image.fromarray(composed, "L").save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
