# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rotas import menu, unidades, categorias, materiais # Importa os módulos isolados

app = FastAPI(title="MasterMat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# A MÁGICA: O main apenas "conecta" as rotas isoladas  
app.include_router(menu.router)
app.include_router(unidades.router)
app.include_router(categorias.router)
app.include_router(materiais.router)
