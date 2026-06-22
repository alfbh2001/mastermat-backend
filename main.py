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
DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def obter_dados_do_banco():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Adicionamos COALESCE(ordem, 0) para evitar que valores nulos quebrem a árvore do Postgres
    query = """
    WITH RECURSIVE menu_arvore AS (
        SELECT id_menu, ordem, id_pai, descricao, funcao, ARRAY[COALESCE(ordem, 0)] AS caminho
        FROM mm_menu
        WHERE id_pai IS NULL
        UNION ALL
        SELECT m.id_menu, m.ordem, m.id_pai, m.descricao, m.funcao, p.caminho || COALESCE(m.ordem, 0)
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
    
    # CORRIGIDO: Agora todas as variáveis internas usam 'linha'
    filhos = [linha for linha in linhas if (linha["id_pai"] == pai_id or str(linha["id_pai"]) == str(pai_id))]
    
    # Ordena tratando possíveis valores None na coluna ordem
    filhos.sort(key=lambda x: x["ordem"] if x["ordem"] is not None else 0)
    
    for filho in filhos:
        node = {
            "id_menu": str(filho["id_menu"]),
            "descricao": filho["descricao"],
            "funcao": filho["funcao"] if filho["funcao"] is not None else "",
            "submenus": estruturar_linhas_em_arvore(linhas, filho["id_menu"])
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
