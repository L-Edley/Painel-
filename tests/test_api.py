from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_pagina_inicial():
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert "Painel Checker" in resposta.text
    assert "/static/css/style.css" in resposta.text
    assert "/static/js/app.js" in resposta.text


def test_arquivos_estaticos():
    assert cliente.get("/static/css/style.css").status_code == 200
    assert cliente.get("/static/js/app.js").status_code == 200
    assert cliente.get("/static/favicon.svg").status_code == 200


def test_health():
    resposta = cliente.get("/api/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_health_alias_raiz():
    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_checagem_em_lote():
    resposta = cliente.post(
        "/api/checar",
        json={
            "itens": [
                "4111111111111111",
                "4532159876543210",
                "   ",
            ]
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()
    assert dados["total"] == 2
    assert dados["aprovados"] == 1
    assert dados["reprovados"] == 1
    assert dados["taxa_aprovacao"] == 50.0
    assert len(dados["resultados"]) == 2
    assert dados["resultados"][0]["item"] == "4111111111111111"


def test_checagem_lista_vazia():
    resposta = cliente.post("/api/checar", json={"itens": []})

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Lista vazia."


def test_checagem_sem_itens_validos():
    resposta = cliente.post("/api/checar", json={"itens": ["   ", ""]})

    assert resposta.status_code == 400
    assert "Nenhum item" in resposta.json()["detail"]


def test_checagem_respeita_limite_do_lote():
    resposta = cliente.post(
        "/api/checar",
        json={"itens": ["4111111111111111"] * 501},
    )

    assert resposta.status_code == 422


def test_gateway_aprovado():
    resposta = cliente.post(
        "/api/gateway/pagar",
        json={"cartao": "4111 1111 1111 1111", "valor": 100},
    )

    assert resposta.status_code == 200

    dados = resposta.json()
    assert dados["status"] == "Aprovado"
    assert dados["codigo"] == 200
    assert dados["autorizacao"].startswith("AUTH_")
    assert dados["final_cartao"] == "1111"


def test_gateway_recusado_por_bandeira():
    resposta = cliente.post(
        "/api/gateway/pagar",
        json={"cartao": "5555555555554444", "valor": 100},
    )

    assert resposta.status_code == 200

    dados = resposta.json()
    assert dados["status"] == "Negado"
    assert dados["codigo"] == 402


def test_gateway_luhn_invalido():
    resposta = cliente.post(
        "/api/gateway/pagar",
        json={"cartao": "4532159876543210", "valor": 100},
    )

    assert resposta.status_code == 200
    assert resposta.json()["codigo"] == 400


def test_gateway_valor_invalido():
    resposta = cliente.post(
        "/api/gateway/pagar",
        json={"cartao": "4111111111111111", "valor": 0},
    )

    assert resposta.status_code == 422
