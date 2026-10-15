"""
Script para iniciar o servidor web FastAPI (Seção 2.1.3 do TCC)
"""

import uvicorn
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO SERVIDOR WEB FASTAPI - MECANISMO DE BUSCA SEMÂNTICA")
    print("Documentação interativa disponível em: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

