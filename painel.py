"""Ponto de entrada de compatibilidade.

Mantenha `uvicorn painel:app --reload` funcionando. A aplicação de verdade
fica no pacote `app`, separada em rotas, serviços e interface.
"""

from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    from app.config import HOST_PADRAO, PORTA_PADRAO

    uvicorn.run(
        "app.main:app",
        host=HOST_PADRAO,
        port=PORTA_PADRAO,
        reload=True,
    )
