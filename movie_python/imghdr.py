# -*- coding: utf-8 -*-
"""
Python 3.14 では標準ライブラリ `imghdr` が無いことがあるため、
Streamlit が `import imghdr` したときに最低限の互換を提供する。

Streamlit は主に `imghdr.what(...)` を使って画像形式推定を行うため、
ここでは PNG / JPEG / GIF / BMP / WEBP / TIFF だけを簡易実装する。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

BytesLike = Union[bytes, bytearray, memoryview]


_PNG_SIG = b"\x89PNG\r\n\x1a\n"
_GIF_SIGS = (b"GIF87a", b"GIF89a")
_BMP_SIG = b"BM"
_WEBP_RIFF = b"RIFF"
_WEBP_WEBP = b"WEBP"
_JPEG_SOI = b"\xff\xd8\xff"
_TIFF_LE = b"II*\x00"
_TIFF_BE = b"MM\x00*"


def _coerce_bytes(file, h: Optional[int] = None) -> Optional[bytes]:
    # file が bytes 系の場合
    if isinstance(file, (bytes, bytearray, memoryview)):
        return bytes(file)

    # imghdr.what(None, data) の形を想定
    if file is None and isinstance(h, (bytes, bytearray, memoryview)):
        return bytes(h)

    # file がパスの場合
    if isinstance(file, (str, Path)):
        path = Path(file)
        with path.open("rb") as f:
            read_n = 32 if h is None else int(h)
            return f.read(read_n)

    # file-like (read メソッド)
    if hasattr(file, "read"):
        read_n = 32 if h is None else int(h)
        return file.read(read_n)

    return None


def what(file, h=None) -> Optional[str]:
    """
    引数の互換性を最小限に満たす what 実装。

    - file: パス文字列 / file-like / bytes / None
    - h: 画像の先頭バイト数（imghdr標準の互換）
         もしくは file が None の場合に渡される bytes
    """
    data = _coerce_bytes(file, h=h if isinstance(h, int) else None)
    # 上の _coerce_bytes は file=None & bytes を扱うために特別分岐している
    if data is None:
        # file=None & h が bytes だったケース（上で None 扱いされるので再判定）
        if file is None and isinstance(h, (bytes, bytearray, memoryview)):
            data = bytes(h)

    if not data:
        return None

    if data.startswith(_PNG_SIG):
        return "png"
    if data.startswith(_JPEG_SOI):
        return "jpeg"
    if data[:6] in _GIF_SIGS:
        return "gif"
    if data.startswith(_BMP_SIG):
        return "bmp"
    if data.startswith(_TIFF_LE) or data.startswith(_TIFF_BE):
        return "tiff"
    # WEBP: RIFF....WEBP
    if data.startswith(_WEBP_RIFF) and len(data) >= 12 and data[8:12] == _WEBP_WEBP:
        return "webp"

    return None


__all__ = ["what"]

