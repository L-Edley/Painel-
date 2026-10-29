import pytest

from app.services.cartao import normalizar_cartao, validar_luhn
from app.services.gateway import autorizar_pagamento


@pytest.mark.parametrize(
    "numero",
    [
        "4111111111111111",
        "4012001023456789",
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
        "4111.1111.1111.1111",
    ],
)
def test_luhn_aceita_numeros_validos(numero):
    assert validar_luhn(numero) is True


@pytest.mark.parametrize(
    "numero",
    [
        "",
        "123",
        "4532159876543210",
        "5162981234567890",
        "abcd",
        "4111111111111112",
        "411111111111111111111111",
    ],
)
def test_luhn_rejeita_numeros_invalidos(numero):
    assert validar_luhn(numero) is False


def test_normalizacao_remove_separadores():
    assert normalizar_cartao(" 4111-1111 1111.1111 ") == "4111111111111111"


def test_gateway_aprova_visa_valido():
    resposta = autorizar_pagamento("4111 1111 1111 1111", 100)

    assert resposta["status"] == "Aprovado"
    assert resposta["codigo"] == 200
    assert resposta["final_cartao"] == "1111"
    assert resposta["autorizacao"].startswith("AUTH_")


def test_gateway_nega_bandeira_nao_simulada():
    resposta = autorizar_pagamento("5555555555554444", 100)

    assert resposta["status"] == "Negado"
    assert resposta["codigo"] == 402


def test_gateway_nega_luhn():
    resposta = autorizar_pagamento("4532159876543210", 100)

    assert resposta["status"] == "Negado"
    assert resposta["codigo"] == 400
