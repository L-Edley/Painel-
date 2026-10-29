"""Rotas que entregam a interface HTML."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, MAX_ITENS_POR_LOTE, TITULO_APP, VERSAO_APP

router = APIRouter(tags=["Interface"])
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "titulo": TITULO_APP,
            "versao": VERSAO_APP,
            "max_itens": MAX_ITENS_POR_LOTE,
        },
    )
