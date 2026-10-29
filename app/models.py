"""Modelos de entrada da API."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.config import MAX_ITENS_POR_LOTE, VALOR_MAXIMO


class PayloadChecagem(BaseModel):
    """Lote de números enviado para a validação de Luhn."""

    model_config = ConfigDict(str_strip_whitespace=True)

    itens: List[str] = Field(
        ...,
        max_length=MAX_ITENS_POR_LOTE,
        description=f"Lista de números de cartão (máximo de {MAX_ITENS_POR_LOTE} itens).",
        examples=[["4111 1111 1111 1111", "4532 1598 7654 3210"]],
    )


class PayloadPagamento(BaseModel):
    """Dados enviados ao gateway simulado."""

    model_config = ConfigDict(str_strip_whitespace=True)

    cartao: str = Field(
        ...,
        max_length=32,
        description="Número do cartão, com ou sem separadores.",
        examples=["4111 1111 1111 1111"],
    )
    valor: float = Field(
        ...,
        gt=0,
        le=VALOR_MAXIMO,
        description="Valor da compra simulada.",
        examples=[100.0],
    )
