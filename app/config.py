"""Configurações centrais do laboratório.

Edite este arquivo para ajustar limites, latência e dados de execução
sem precisar mexer nas rotas ou na interface.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TITULO_APP = "Painel Checker - Laboratório Acadêmico"
VERSAO_APP = "2.0.0"

HOST_PADRAO = "127.0.0.1"
PORTA_PADRAO = 8000

# Simula latência de rede em cada item do lote.
LATENCIA_SIMULADA = 0.2

# Limites de entrada para evitar lotes absurdos.
MAX_ITENS_POR_LOTE = 500
MAX_CONCORRENCIA = 50

# Valor máximo aceito pelo gateway simulado.
VALOR_MAXIMO = 1_000_000.0
