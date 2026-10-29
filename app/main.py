"""Ponto de entrada da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, TITULO_APP, VERSAO_APP
from app.routers import api, pages

app = FastAPI(
    title=TITULO_APP,
    version=VERSAO_APP,
    description=(
        "Laboratório local para validação de Luhn e simulação de gateway "
        "de pagamento. Não processa pagamentos reais."
    ),
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)
app.include_router(pages.router)
app.include_router(api.router)

# Alias comum para monitoramento; a rota documentada continua em /api/health.
app.add_api_route("/health", api.health, include_in_schema=False)
