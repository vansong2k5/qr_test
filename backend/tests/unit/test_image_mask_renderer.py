from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from app.storage.local import storage
from app.utils.qr_renderer import ImageMaskQrRenderer, decode_qr_image


def test_renderer_without_mask(tmp_path: Path):
    storage.base_dir = tmp_path
    renderer = ImageMaskQrRenderer(
        data="https://example.com",
        ecc="H",
        fg_color="#000000",
        bg_color="#FFFFFF",
        margin=4,
        size=256,
        mask_bytes=None,
        logo_bytes=None,
    )
    result = renderer.render()
    png_file = tmp_path / result.png_path
    assert png_file.exists()


def test_renderer_decode_roundtrip(tmp_path: Path):
    storage.base_dir = tmp_path
    renderer = ImageMaskQrRenderer(
        data='{"product": "A"}',
        ecc="H",
        fg_color="#111111",
        bg_color="#FFFFFF",
        margin=4,
        size=256,
        mask_bytes=None,
        logo_bytes=None,
    )
    result = renderer.render()
    data = (tmp_path / result.png_path).read_bytes()
    decoded = decode_qr_image(data)
    if decoded is None:
        pytest.skip("OpenCV not available in test environment")
    assert decoded == '{"product": "A"}'


def test_renderer_raises_on_empty_mask(tmp_path: Path):
    storage.base_dir = tmp_path
    img = Image.new('L', (32, 32), 255)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    renderer = ImageMaskQrRenderer(
        data="hello",
        ecc="H",
        fg_color="#000000",
        bg_color="#FFFFFF",
        margin=4,
        size=128,
        mask_bytes=buf.getvalue(),
        logo_bytes=None,
    )
    with pytest.raises(ValueError):
        renderer.render()
