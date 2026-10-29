"""Rotas da API."""

from fastapi import APIRouter, HTTPException

from app.models import PayloadChecagem, PayloadPagamento
from app.services.checagem import processar_lote
from app.services.gateway import autorizar_pagamento

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/health", summary="Verifica se a API está no ar")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/checar", summary="Valida uma lista de cartões com Luhn")
async def executar_checagem(payload: PayloadChecagem) -> dict:
    if not payload.itens:
        raise HTTPException(status_code=400, detail="Lista vazia.")

    if not any(item.strip() for item in payload.itens):
        raise HTTPException(
            status_code=400,
            detail="Nenhum item válido informado.",
        )

    return await processar_lote(payload.itens)


@router.post("/gateway/pagar", summary="Gateway de pagamento simulado")
async def processar_pagamento(payload: PayloadPagamento) -> dict:
    return autorizar_pagamento(payload.cartao, payload.valor)
