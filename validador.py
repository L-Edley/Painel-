"""Varredura didática de rotas comuns em um alvo local.

Uso:
    python validador.py
    python validador.py --alvo http://127.0.0.1:8000

Por segurança, alvos fora de localhost exigem a flag --allow-remote.
Use apenas em sistemas que você tem autorização para testar.
"""

from __future__ import annotations

import argparse
import os
import sys
from urllib.parse import urlparse

import httpx

ROTAS_COMUNS = [
    "/api/pay",
    "/api/checkout",
    "/api/gateway/pagar",
    "/checkout",
    "/pagar",
    "/api/v1/pagamento",
]


def configurar_saida() -> None:
    """Evita UnicodeEncodeError no console do Windows."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def alvo_local(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost", "::1"}


def mapear_alvo(alvo: str, timeout: float = 3.0) -> list[dict]:
    """Testa as rotas e devolve o que foi encontrado."""

    alvo = alvo.rstrip("/")
    print(f"[*] Iniciando varredura contra: {alvo}\n")

    resultados: list[dict] = []

    with httpx.Client(timeout=timeout, follow_redirects=False) as cliente:
        for rota in ROTAS_COMUNS:
            url = f"{alvo}{rota}"

            try:
                resposta = cliente.post(url, json={})
            except httpx.RequestError as exc:
                print(f"[!] Servidor inacessível em {rota}: {exc}")
                break

            if resposta.status_code == httpx.codes.NOT_FOUND:
                print(f"[-] Rota não encontrada: {rota}")
                resultados.append(
                    {"rota": rota, "encontrada": False, "status": 404}
                )
                continue

            print(f"[+] Rota encontrada: {url} (HTTP {resposta.status_code})")

            texto = " ".join(resposta.text.split())
            if len(texto) > 300:
                texto = f"{texto[:300]}..."

            print(f"    Resposta: {texto or '(vazia)'}\n")
            resultados.append(
                {
                    "rota": rota,
                    "encontrada": True,
                    "status": resposta.status_code,
                    "resposta": texto,
                }
            )

    return resultados


def main() -> None:
    configurar_saida()

    parser = argparse.ArgumentParser(
        description="Varredura didática de rotas de pagamento em ambiente local."
    )
    parser.add_argument(
        "--alvo",
        default=os.getenv("ALVO_URL", "http://127.0.0.1:8000"),
        help="URL base do alvo (padrão: http://127.0.0.1:8000).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Timeout por requisição em segundos (padrão: 3).",
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

    mapear_alvo(args.alvo, args.timeout)


if __name__ == "__main__":
    main()
