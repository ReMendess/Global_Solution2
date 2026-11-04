"""Persistência das imagens enviadas: validação, gravação e metadados (ADR-005)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from app.core.config import get_settings
from app.core.constants import ALLOWED_IMAGE_TYPES
from app.core.exceptions import PayloadTooLargeError, UnprocessableError

if TYPE_CHECKING:
    from fastapi import UploadFile


@dataclass(slots=True)
class SavedImage:
    """Resultado da gravação de uma imagem em disco."""

    file_path: str
    content_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None


def _image_size(data: bytes) -> tuple[int | None, int | None]:
    """Lê a dimensão da imagem sem falhar quando o arquivo é inválido."""
    try:
        from io import BytesIO

        from PIL import Image

        with Image.open(BytesIO(data)) as imagem:  # pragma: no cover - depende do arquivo
            return imagem.width, imagem.height
    except Exception:  # noqa: BLE001 - metadado opcional, nunca bloqueia o registro
        return None, None


def save_upload(upload: UploadFile) -> SavedImage:
    """Valida e grava a imagem enviada, devolvendo o caminho relativo salvo."""
    settings = get_settings()

    content_type = upload.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        permitidos = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
        raise UnprocessableError(f"Formato de imagem não suportado. Use: {permitidos}.")

    data = upload.file.read(settings.max_upload_bytes + 1)
    if not data:
        raise UnprocessableError("O arquivo de imagem está vazio.")
    if len(data) > settings.max_upload_bytes:
        raise PayloadTooLargeError(f"A imagem excede o limite de {settings.max_upload_mb} MB.")

    destino = settings.resolved_upload_dir
    destino.mkdir(parents=True, exist_ok=True)

    nome_arquivo = f"{uuid4().hex}{ALLOWED_IMAGE_TYPES[content_type]}"
    (destino / nome_arquivo).write_bytes(data)

    width, height = _image_size(data)
    return SavedImage(
        file_path=nome_arquivo,
        content_type=content_type,
        size_bytes=len(data),
        width=width,
        height=height,
    )
