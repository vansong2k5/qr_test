from __future__ import annotations

import io
import uuid
from dataclasses import dataclass

from PIL import Image, ImageColor, ImageOps
import qrcode
from qrcode.image.svg import SvgPathImage

from ..storage.local import storage


@dataclass
class RenderResult:
    code: str
    png_path: str
    svg_path: str
    mask_path: str | None


QUIET_ZONE = 4


def _load_mask(mask_bytes: bytes | None, size: int) -> Image.Image | None:
    if not mask_bytes:
        return None
    image = Image.open(io.BytesIO(mask_bytes)).convert("L")
    image = ImageOps.invert(image)
    image = image.resize((size, size))
    threshold = 128
    return image.point(lambda x: 255 if x > threshold else 0, mode="1")


def render_qr(
    data: str,
    *,
    mask_bytes: bytes | None = None,
    foreground: str = "#000000",
    background: str = "#FFFFFF",
    error_correction: str = "H",
) -> RenderResult:
    qr = qrcode.QRCode(
        error_correction={
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
        border=QUIET_ZONE,
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    size = len(matrix)

    mask = _load_mask(mask_bytes, size) if mask_bytes else None

    img = Image.new("RGB", (size + QUIET_ZONE * 2, size + QUIET_ZONE * 2), background)
    pixels = img.load()

    fg_color = ImageColor.getrgb(foreground)
    for y in range(size):
        for x in range(size):
            value = matrix[y][x]
            target = (x + QUIET_ZONE, y + QUIET_ZONE)
            if value:
                if mask and not mask.getpixel((x, y)):
                    continue
                pixels[target] = fg_color

    buffer = io.BytesIO()
    img = img.resize((img.size[0] * 10, img.size[1] * 10), resample=Image.NEAREST)
    img.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    svg_buffer = io.BytesIO()
    qr.make_image(image_factory=SvgPathImage, fill_color=foreground, back_color=background).save(svg_buffer)
    svg_bytes = svg_buffer.getvalue()

    code = uuid.uuid4().hex
    png_path = storage.save(filename=f"qr/{code}.png", data=png_bytes)
    svg_path = storage.save(filename=f"qr/{code}.svg", data=svg_bytes)
    mask_path = None
    if mask_bytes:
        mask_path = storage.save(filename=f"qr/{code}_mask.png", data=mask_bytes)
    return RenderResult(code=code, png_path=png_path, svg_path=svg_path, mask_path=mask_path)
