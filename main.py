from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI()

# Permite que o seu HTML acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cole aqui a String de Conexão do Neon
DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def obter_dados_do_banco():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
    WITH RECURSIVE menu_arvore AS (
        SELECT id_menu, ordem, id_pai, descricao, nivel, ARRAY[ordem] AS caminho
        FROM mm_menu
        WHERE id_pai IS NULL
        UNION ALL
        SELECT m.id_menu, m.ordem, m.id_pai, m.descricao, m.nivel, p.caminho || m.ordem
        FROM mm_menu m
        INNER JOIN menu_arvore p ON m.id_pai = p.id_menu
    )
    SELECT id_menu, id_pai, descricao, nivel FROM menu_arvore ORDER BY caminho;
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def estruturar_linhas_em_arvore(linhas, pai_id=None):
    arvore = []
    filhos = [linha for linha in lines if linha["id_pai"] == pai_id]
    for child in filhos:
        node = {
            "descricao": child["descricao"],
            "nivel": child["nivel"],
            "submenus": estruturar_linhas_em_arvore(linhas, child["id_menu"])
        }
        arvore.append(node)
    return arvore

@app.get("/api/menu")
def get_menu():
    try:
        linhas_do_banco = obter_dados_do_banco()
        return estruturar_linhas_em_arvore(linhas_do_banco)
    except Exception as e:
        return {"erro": str(e)}
