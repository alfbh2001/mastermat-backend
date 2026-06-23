from fastapi import APIRouter
import psycopg2
from psycopg2.extras import RealDictCursor

# Criamos o roteador do menu
router = APIRouter(prefix="/api/menu", tags=["Menu"])

DATABASE_URL = "SUA_URL_DO_NEON_AQUI"

def obter_dados_do_banco():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
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
    filhos = [linha for linha in linhas if (linha["id_pai"] == pai_id or str(linha["id_pai"]) == str(pai_id))]
    filhos.sort(key=lambda x: x["ordem"] if x["ordem"] is not None else 0)
    for child in filhos:
        node = {
            "id_menu": str(child["id_menu"]),
            "descricao": child["descricao"],
            "funcao": child["funcao"] if child["funcao"] is not None else "",
            "submenus": estruturar_linhas_em_arvore(linhas, child["id_menu"])
        }
        arvore.append(node)
    return arvore

@router.get("") # Fica vazio porque o prefixo do arquivo já é /api/menu
def get_menu():
    try:
        linhas_do_banco = obter_dados_do_banco()
        menu_estruturado = estruturar_linhas_em_arvore(linhas_do_banco)
        return menu_estruturado
    except Exception as e:
        return {"erro": str(e)}
