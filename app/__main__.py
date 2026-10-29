"""Permite iniciar o servidor com `python -m app`."""

import uvicorn

from app.config import HOST_PADRAO, PORTA_PADRAO

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST_PADRAO,
        port=PORTA_PADRAO,
        reload=True,
    )
