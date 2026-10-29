"""Envia cartões de demonstração para o gateway local.

Uso:
    python disparador.py
    python disparador.py --alvo http://127.0.0.1:8000/api/gateway/pagar

Por segurança, alvos fora de localhost exigem a flag --allow-remote.
Use apenas em sistemas que você tem autorização para testar.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from urllib.parse import urlparse

import httpx

CABECALHOS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AcademicLab/2.0",
}

CARTOES_DEMO = [
    "4012001023456789",
    "4532159876543210",
    "5162981234567890",
]

VALOR_DEMO = 100.00


def configurar_saida() -> None:
    """Evita problemas de encoding no console do Windows."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def alvo_local(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost", "::1"}


async def disparar_requisicao(
    cliente: httpx.AsyncClient, url: str, cartao: str
) -> dict:
    payload = {
        "cartao": cartao,
        "valor": VALOR_DEMO,
        "validade": "12/28",
        "cvv": "123",
    }

    try:
        resposta = await cliente.post(url, json=payload)
    except httpx.RequestError as exc:
        return {
            "cartao": cartao,
            "status_http": "Erro de conexão",
            "retorno": str(exc),
        }

    try:
        retorno = resposta.json()
    except ValueError:
        retorno = resposta.text

    return {
        "cartao": cartao,
        "status_http": resposta.status_code,
        "retorno": retorno,
    }


async def main() -> None:
    configurar_saida()

    parser = argparse.ArgumentParser(
        description="Dispara cartões de demonstração contra um gateway local."
    )
    parser.add_argument(
        "--alvo",
        default=os.getenv(
            "ALVO_URL",
            "http://127.0.0.1:8000/api/gateway/pagar",
        ),
        help="URL do gateway (padrão: http://127.0.0.1:8000/api/gateway/pagar).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout por requisição em segundos (padrão: 5).",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Permite alvo remoto. Use apenas com autorização.",
    )
    args = parser.parse_args()

    if urlparse(args.alvo).scheme not in {"http", "https"}:
        parser.error("Informe uma URL com http:// ou https://.")

    if not alvo_local(args.alvo) and not args.allow_remote:
        parser.error(
            "Alvo remoto bloqueado por padrão. "
            "Use --allow-remote apenas em ambiente autorizado."
        )

    print(f"[*] Iniciando disparos contra: {args.alvo}")
    inicio = time.perf_counter()

    semaforo = asyncio.Semaphore(5)

    async def requisicao_controlada(
        cliente: httpx.AsyncClient, cartao: str
    ) -> dict:
        async with semaforo:
            return await disparar_requisicao(cliente, args.alvo, cartao)

    async with httpx.AsyncClient(
        headers=CABECALHOS, timeout=args.timeout
    ) as cliente:
        tarefas = [
            requisicao_controlada(cliente, cartao)
            for cartao in CARTOES_DEMO
        ]
        resultados = await asyncio.gather(*tarefas)

    duracao = time.perf_counter() - inicio
    print(f"\n[+] Processo concluído em {duracao:.2f} segundos.\n")
    print("-" * 60)

    for resultado in resultados:
        retorno = resultado["retorno"]
        if isinstance(retorno, (dict, list)):
            retorno = json.dumps(retorno, ensure_ascii=False)
        print(
            f"Cartão: {resultado['cartao']} | "
            f"HTTP: {resultado['status_http']} | "
            f"Resposta: {retorno}"
        )

    print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
