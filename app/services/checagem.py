"""Processamento assíncrono do lote de cartões."""

from __future__ import annotations

import asyncio
from typing import Optional

from app.config import LATENCIA_SIMULADA, MAX_CONCORRENCIA
from app.services.cartao import validar_luhn


async def processar_item(
    item: str, semaforo: asyncio.Semaphore
) -> Optional[dict]:
    """Valida um item isolado, simulando latência de rede."""

    item_limpo = item.strip()
    if not item_limpo:
        return None

    async with semaforo:
        await asyncio.sleep(LATENCIA_SIMULADA)

    if validar_luhn(item_limpo):
        return {
            "item": item_limpo,
            "status": "Aprovado",
            "valido": True,
            "motivo": "Passou na validação de Luhn (sintaxe válida).",
        }

    return {
        "item": item_limpo,
        "status": "Reprovado",
        "valido": False,
        "motivo": "Falha no dígito verificador.",
    }


async def processar_lote(itens: list[str]) -> dict:
    """Processa todos os itens com concorrência limitada."""

    semaforo = asyncio.Semaphore(MAX_CONCORRENCIA)
    tarefas = [processar_item(item, semaforo) for item in itens]
    resultados = await asyncio.gather(*tarefas)

    filtrados = [resultado for resultado in resultados if resultado is not None]
    aprovados = sum(1 for item in filtrados if item["status"] == "Aprovado")
    reprovados = len(filtrados) - aprovados
    total = len(filtrados)

    return {
        "total": total,
        "aprovados": aprovados,
        "reprovados": reprovados,
        "taxa_aprovacao": round((aprovados / total) * 100, 1) if total else 0.0,
        "resultados": filtrados,
    }
