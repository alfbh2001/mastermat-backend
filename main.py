from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Permite que o seu HTML acesse a API tranquilamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ Sua String de Conexão do Neon (Mantenha a sua aqui)
DATABASE_URL = "postgresql://usuario:senha@seu-servidor.neon.tech/neondb?sslmode=require"

def obter_dados_do_banco():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query ajustada para trazer os campos oficiais e ordenar por 'ordem' dentro da hierarquia
    query = """
    WITH RECURSIVE menu_arvore AS (
        SELECT id_menu, ordem, id_pai, descricao, funcao, ARRAY[ordem] AS caminho
        FROM mm_menu
        WHERE id_pai IS NULL
        UNION ALL
        SELECT m.id_menu, m.ordem, m.id_pai, m.descricao, m.funcao, p.caminho || m.ordem
        FROM mm_menu m
        INNER JOIN menu_arvore p ON m.id_pai = p.id_menu
    )
    SELECT id_menu, id_pai, descricao, funcao, ordem FROM menu_arvore ORDER BY caminho;
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def estruturar_linhas_em_arvore(linhas, pai_id=None):
    arvore = []
    
    # Filtra os filhos do nó atual e garante que fiquem estritamente ordenados pela coluna 'ordem'
    filhos = [linha for linha in linhas if linha["id_pai"] == pai_id]
    filhos.sort(key=lambda x: x["ordem"] if x["ordem"] is not None else 0)
    
    for filho in filhos:
        # Monta o nó incluindo o novo campo 'funcao'
        node = {
            "id_menu": filho["id_menu"],
            "descricao": filho["descricao"],
            "funcao": filho["funcao"], # Nome da tela que o JS irá disparar
            "submenus": estruturar_linhas_em_arvore(linhas, filho["id_menu"]) # Disparo recursivo
        }
        arvore.append(node)
        
    return arvore

@app.get("/api/menu")
def get_menu():
    try:
        linhas_do_banco = obter_dados_do_banco()
        menu_estruturado = estruturar_linhas_em_arvore(linhas_do_banco)
        return menu_estruturado
    except Exception as e:
        return {"erro": str(e)}
