"""Gateway de pagamento simulado.

A regra é propositalmente simples para fins didáticos:
- precisa passar no Luhn;
- precisa começar com 4 para ser aprovado.
"""

from __future__ import annotations

import secrets

from app.services.cartao import normalizar_cartao, validar_luhn


def autorizar_pagamento(cartao: str, valor: float) -> dict:
    """Simula a resposta de um emissor de cartão."""

    numero = normalizar_cartao(cartao)

    if not validar_luhn(numero):
        return {
            "status": "Negado",
            "codigo": 400,
            "motivo": "Cartão inválido (Luhn falhou).",
        }

    if not numero.startswith("4"):
        return {
            "status": "Negado",
            "codigo": 402,
            "motivo": "Transação recusada pelo emissor / 3DS requerido.",
        }

    return {
        "status": "Aprovado",
        "codigo": 200,
        "autorizacao": f"AUTH_{secrets.randbelow(900_000) + 100_000}",
        "valor": round(valor, 2),
        "final_cartao": numero[-4:],
    }
