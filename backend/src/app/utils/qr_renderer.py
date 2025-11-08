"""Render QR tuân theo mask ảnh với giải thích tiếng Việt."""
from __future__ import annotations

import io
import uuid
from dataclasses import dataclass
from typing import Iterable

import qrcode
from PIL import Image, ImageColor, ImageFilter
from qrcode.exceptions import DataOverflowError

from app.storage.local import storage

try:  # pragma: no cover - phụ thuộc optional
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore

try:  # pragma: no cover
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore

ECC_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


@dataclass
class RenderResult:
    code_id: uuid.UUID
    version: int
    ecc: str
    png_path: str
    svg_path: str
    mask_path: str | None
    logo_path: str | None


class ImageMaskQrRenderer:
    """Renderer tuân thủ mask ảnh.

    Thuật toán:
    1. Chuyển ảnh mask về grayscale rồi nhị phân bằng Otsu. Pixel đen thể hiện vùng được đặt module.
    2. Tạo QR phiên bản nhỏ nhất -> nếu các module trùng vào vùng trắng => mask quá thưa. Khi đó lần lượt tăng version (mật độ module dày hơn).
    3. Nếu đã tới version 40 mà vẫn xung đột, ta nới lỏng mask bằng phép giãn (dilation) => giảm yêu cầu hình dạng.
    4. Khi thành công, render PNG/SVG và (tùy chọn) chèn logo ở giữa.
    """

    def __init__(
        self,
        *,
        data: str,
        ecc: str,
        fg_color: str,
        bg_color: str,
        margin: int,
        size: int,
        mask_bytes: bytes | None,
        logo_bytes: bytes | None,
        threshold: int | None = None,
    ):
        self.data = data
        self.ecc = ecc if ecc in ECC_MAP else "H"
        self.fg_color = ImageColor.getrgb(fg_color)
        self.bg_color = ImageColor.getrgb(bg_color)
        self.margin = margin
        self.target_size = size
        self.mask_bytes = mask_bytes
        self.logo_bytes = logo_bytes
        self.threshold = threshold

    def render(self) -> RenderResult:
        mask_image = self._load_mask()
        version = None
        dilation_passes = 0
        matrix = None
        code_uuid = uuid.uuid4()
        while True:
            try_versions = self._candidate_versions(version)
            success = False
            for version_candidate in try_versions:
                matrix = self._build_matrix(version_candidate)
                if mask_image is None:
                    version = version_candidate
                    success = True
                    break
                mask_bool = self._mask_for_matrix(mask_image, len(matrix))
                self._ensure_finder_allowed(mask_bool)
                conflicts = self._count_conflicts(matrix, mask_bool)
                if conflicts == 0:
                    version = version_candidate
                    success = True
                    break
            if success:
                break
            if mask_image is not None and dilation_passes < 3:
                mask_image = mask_image.filter(ImageFilter.MaxFilter(size=3))
                dilation_passes += 1
                version = None
                continue
            raise ValueError("Mask không đủ mật độ để render QR")

        assert matrix is not None and version is not None
        image = self._render_png(matrix, mask_image)
        if self.logo_bytes:
            image = self._overlay_logo(image)
        image = image.resize((self.target_size, self.target_size), Image.NEAREST)

        png_bytes = io.BytesIO()
        image.save(png_bytes, format="PNG")
        png_path = storage.save(f"qr/{code_uuid.hex}.png", png_bytes.getvalue())

        svg_bytes = self._render_svg(matrix, mask_image)
        svg_path = storage.save(f"qr/{code_uuid.hex}.svg", svg_bytes)

        mask_path = None
        if self.mask_bytes:
            mask_path = storage.save(f"qr/{code_uuid.hex}_mask.png", self.mask_bytes)

        logo_path = None
        if self.logo_bytes:
            logo_path = storage.save(f"qr/{code_uuid.hex}_logo.png", self.logo_bytes)

        return RenderResult(
            code_id=code_uuid,
            version=version,
            ecc=self.ecc,
            png_path=png_path,
            svg_path=svg_path,
            mask_path=mask_path,
            logo_path=logo_path,
        )

    def _load_mask(self) -> Image.Image | None:
        if not self.mask_bytes:
            return None
        image = Image.open(io.BytesIO(self.mask_bytes)).convert("L")
        threshold = self.threshold or self._otsu_threshold(image)
        binary = image.point(lambda x: 0 if x < threshold else 255, mode="L")
        return binary

    @staticmethod
    def _otsu_threshold(image: Image.Image) -> int:
        histogram = image.histogram()
        total = sum(histogram)
        sum_total = sum(i * histogram[i] for i in range(256))
        sum_b = 0.0
        weight_b = 0.0
        max_var = 0.0
        threshold = 0
        for i in range(256):
            weight_b += histogram[i]
            if weight_b == 0:
                continue
            weight_f = total - weight_b
            if weight_f == 0:
                break
            sum_b += i * histogram[i]
            mean_b = sum_b / weight_b
            mean_f = (sum_total - sum_b) / weight_f
            var_between = weight_b * weight_f * (mean_b - mean_f) ** 2
            if var_between > max_var:
                max_var = var_between
                threshold = i
        return threshold

    def _candidate_versions(self, start: int | None) -> Iterable[int]:
        start_version = start or 1
        return range(start_version, 41)

    def _build_matrix(self, version: int) -> list[list[int]]:
        qr = qrcode.QRCode(
            version=version,
            error_correction=ECC_MAP[self.ecc],
            box_size=1,
            border=self.margin,
        )
        try:
            qr.add_data(self.data)
            qr.make(fit=False)
        except DataOverflowError:
            if version >= 40:
                raise
            return self._build_matrix(version + 1)
        return qr.get_matrix()

    def _mask_for_matrix(self, mask_image: Image.Image, module_size: int) -> list[list[bool]]:
        resized = mask_image.resize((module_size, module_size), Image.NEAREST)
        pixels = resized.load()
        return [[pixels[x, y] < 128 for x in range(module_size)] for y in range(module_size)]

    @staticmethod
    def _ensure_finder_allowed(mask_bool: list[list[bool]]) -> None:
        size = len(mask_bool)
        finder_coords = [(0, 0), (size - 7, 0), (0, size - 7)]
        for (x, y) in finder_coords:
            for row in range(y, y + 7):
                for col in range(x, x + 7):
                    mask_bool[row][col] = True

    @staticmethod
    def _count_conflicts(matrix: list[list[int]], mask_bool: list[list[bool]]) -> int:
        conflicts = 0
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if value and not mask_bool[y][x]:
                    conflicts += 1
        return conflicts

    def _render_png(self, matrix: list[list[int]], mask_image: Image.Image | None) -> Image.Image:
        size = len(matrix)
        canvas = Image.new("RGB", (size + self.margin * 2, size + self.margin * 2), self.bg_color)
        pixels = canvas.load()
        mask_bool = None
        if mask_image is not None:
            mask_bool = self._mask_for_matrix(mask_image, size)
            self._ensure_finder_allowed(mask_bool)
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if not value:
                    continue
                if mask_bool is not None and not mask_bool[y][x]:
                    continue
                pixels[x + self.margin, y + self.margin] = self.fg_color
        return canvas

    def _overlay_logo(self, image: Image.Image) -> Image.Image:
        logo = Image.open(io.BytesIO(self.logo_bytes)).convert("RGBA")
        target = min(image.size) // 4
        logo.thumbnail((target, target), Image.LANCZOS)
        x = (image.width - logo.width) // 2
        y = (image.height - logo.height) // 2
        image = image.convert("RGBA")
        image.paste(logo, (x, y), logo)
        return image.convert("RGB")

    def _render_svg(self, matrix: list[list[int]], mask_image: Image.Image | None) -> bytes:
        size = len(matrix)
        mask_bool = None
        if mask_image is not None:
            mask_bool = self._mask_for_matrix(mask_image, size)
            self._ensure_finder_allowed(mask_bool)
        scale = 4
        rects = []
        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                if not value:
                    continue
                if mask_bool is not None and not mask_bool[y][x]:
                    continue
                rect = (
                    f'<rect x="{(x + self.margin) * scale}" y="{(y + self.margin) * scale}" '
                    f'width="{scale}" height="{scale}" fill="rgb{self.fg_color}" />'
                )
                rects.append(rect)
        width = (size + self.margin * 2) * scale
        height = (size + self.margin * 2) * scale
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            f'<rect width="100%" height="100%" fill="rgb{self.bg_color}" />' + "".join(rects) + "</svg>"
        )
        return svg.encode("utf-8")


def decode_qr_image(data: bytes) -> str | None:
    """Giải mã QR bằng OpenCV nếu khả dụng."""
    if cv2 is None or np is None:  # type: ignore
        return None
    arr = np.frombuffer(data, dtype=np.uint8)  # type: ignore
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)  # type: ignore
    detector = cv2.QRCodeDetector()  # type: ignore
    value, _, _ = detector.detectAndDecode(img)  # type: ignore
    return value or None
