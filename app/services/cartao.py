"""Normalização e validação de números de cartão."""

from __future__ import annotations

import re


def normalizar_cartao(valor: str) -> str:
    """Remove espaços, hífens e pontos usados como separadores.

    Letras e outros caracteres são mantidos de propósito para que a
    validação possa rejeitá-los em vez de "corrigir" a entrada.
    """

    return re.sub(r"[\s\-\.]+", "", str(valor or "")).strip()


def validar_luhn(valor: str) -> bool:
    """Valida o dígito verificador usando o algoritmo de Luhn.

    Aceita números de 13 a 19 dígitos, com ou sem separadores.
    """

    numero = normalizar_cartao(valor)

    if not numero.isdigit() or not 13 <= len(numero) <= 19:
        return False

    total = 0
    for indice, caractere in enumerate(reversed(numero)):
        digito = int(caractere)
        if indice % 2 == 1:
            digito *= 2
            if digito > 9:
                digito -= 9
        total += digito

    return total % 10 == 0


def mascarar_cartao(valor: str) -> str:
    """Retorna apenas os quatro últimos dígitos, útil para logs."""

    numero = normalizar_cartao(valor)
    if len(numero) <= 4:
        return numero
    return f"{'*' * (len(numero) - 4)}{numero[-4:]}"
