"""Criptografia de recibos de avaliação; o identificador do aluno não fica na resposta."""
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    # Deriva uma chave válida do segredo de aplicação. SECRET_KEY deve ser estável,
    # secreta e mantida em backup seguro; trocá-la impede abrir os recibos existentes.
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_evaluation_id(value):
    return _fernet().encrypt(str(value).encode("utf-8")).decode("ascii")


def decrypt_evaluation_id(value):
    try:
        return _fernet().decrypt(value.encode("ascii"), ttl=None).decode("utf-8")
    except (InvalidToken, ValueError, UnicodeError):
        return None
