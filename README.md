# Painel Checker & Gateway

Laboratório acadêmico local para validar números de cartão com o algoritmo de
Luhn e simular respostas de um gateway de pagamento.

> Este projeto é uma simulação. Ele não consulta emissores, não processa
> pagamentos reais e não deve ser apontado para sistemas de terceiros.

## Estrutura

```text
Painel/
├── app/
│   ├── main.py              # cria o FastAPI e monta rotas/estáticos
│   ├── config.py            # limites, latência, host e porta
│   ├── models.py            # modelos de entrada (Pydantic)
│   ├── routers/
│   │   ├── api.py           # /api/checar, /api/gateway/pagar, /api/health
│   │   └── pages.py         # entrega o HTML
│   ├── services/
│   │   ├── cartao.py        # normalização + algoritmo de Luhn
│   │   ├── gateway.py       # regra do gateway simulado
│   │   └── checagem.py      # processamento assíncrono do lote
│   ├── templates/
│   │   └── index.html       # estrutura visual da página
│   └── static/
│       ├── css/style.css    # estilos
│       ├── js/app.js        # comportamento da interface
│       └── favicon.svg
├── tests/                   # testes automatizados
├── painel.py                # compatibilidade: `uvicorn painel:app`
├── validador.py             # varredura didática de rotas locais
├── disparador.py            # disparos de demonstração contra o gateway local
├── requirements.txt
└── README.md
```

## Como executar

```bash
python -m pip install -r requirements.txt
python -m uvicorn painel:app --reload
```

Também funciona com:

```bash
python -m app
```

Abra <http://127.0.0.1:8000>. A documentação automática da API fica em
<http://127.0.0.1:8000/docs>.

No Windows, também é possível dar dois cliques em `iniciar.bat`.

## Onde editar

| O que mudar | Arquivo |
|---|---|
| Textos, campos e estrutura da tela | `app/templates/index.html` |
| Cores, espaçamento e layout | `app/static/css/style.css` |
| Comportamento da tela, validações e chamadas | `app/static/js/app.js` |
| Rotas da API | `app/routers/api.py` |
| Regras de cartão/Luhn | `app/services/cartao.py` |
| Regra do gateway | `app/services/gateway.py` |
| Limites, latência, host e porta | `app/config.py` |
| Modelos de entrada | `app/models.py` |

## Endpoints

### `POST /api/checar`

```json
{
  "itens": [
    "4111 1111 1111 1111",
    "4532 1598 7654 3210"
  ]
}
```

Resposta:

```json
{
  "total": 2,
  "aprovados": 1,
  "reprovados": 1,
  "taxa_aprovacao": 50.0,
  "resultados": [
    {
      "item": "4111 1111 1111 1111",
      "status": "Aprovado",
      "valido": true,
      "motivo": "Passou na validação de Luhn (sintaxe válida)."
    },
    {
      "item": "4532 1598 7654 3210",
      "status": "Reprovado",
      "valido": false,
      "motivo": "Falha no dígito verificador."
    }
  ]
}
```

### `POST /api/gateway/pagar`

```json
{
  "cartao": "4111 1111 1111 1111",
  "valor": 100.00
}
```

A simulação aprova cartões que passam no Luhn e começam com `4`. Os demais
recebem `codigo` 400 (Luhn inválido) ou 402 (recusado pelo emissor).

### `GET /api/health`

```json
{ "status": "ok" }
```

Também existe o alias `GET /health`, útil para monitoramento.

## Testes

```bash
python -m pytest -q
```

## Scripts auxiliares

Os dois scripts apontam para `127.0.0.1:8000` por padrão e bloqueiam alvos
remotos, a menos que `--allow-remote` seja passado explicitamente.

```bash
python validador.py
python validador.py --alvo http://127.0.0.1:8000 --timeout 2

python disparador.py
python disparador.py --alvo http://127.0.0.1:8000/api/gateway/pagar
```

## Cartões de exemplo

| Número | Luhn | Gateway |
|---|---|---|
| `4111 1111 1111 1111` | válido | aprovado |
| `4012 0010 2345 6789` | válido | aprovado |
| `5555 5555 5555 4444` | válido | negado (prefixo diferente de 4) |
| `4532 1598 7654 3210` | inválido | negado (Luhn) |
