"""QR code helpers for markers. The printed code is a URL, not a bare code (Blueprint, Section 0)."""

import base64
from io import BytesIO

import qrcode
from django.conf import settings


def marker_url(marker) -> str:
    return f"{settings.PLAY_BASE_URL}{marker.scan_path}"


def qr_png_bytes(data: str, box_size: int = 10) -> bytes:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b1a14", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def qr_data_uri(data: str, box_size: int = 10) -> str:
    return "data:image/png;base64," + base64.b64encode(qr_png_bytes(data, box_size)).decode()
