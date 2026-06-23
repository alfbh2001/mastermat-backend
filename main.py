from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Permite que o seu frontend (Netlify ou local) acesse a API sem bloqueios de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ COLE A SUA STRING DE CONEXÃO DO NEON AQUI
DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Modelo de validação para o Cadastro de Unidades
class UnidadeSchema(BaseModel):
    id_unidade: Optional[str] = None
    cod_unidade: str
    desc_unidade: str


# ==============================================================================
# 1. FUNÇÕES AUXILIARES E ROTAS DO MENU DINÂMICO
# ==============================================================================

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
    
    # Filtra os filhos tratando strings/UUIDs perfeitamente
    filhos = [linha for linha in linhas if (linha["id_pai"] == pai_id or str(linha["id_pai"]) == str(pai_id))]
    
    # Ordena tratando possíveis valores nulos (None) na coluna ordem
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


# ==============================================================================
# 2. ROTAS DO CADASTRO DE UNIDADES (TABELA: mm_unidade)
# ==============================================================================

# ROTA A: Listar todas as unidades para alimentar o Grid inferior
@app.get("/api/unidades")
def listar_unidades():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Seleciona os campos oficiais ordenando em ordem alfabética pelo código da unidade
        cursor.execute("SELECT id_unidade, cod_unidade, desc_unidade FROM mm_unidade ORDER BY cod_unidade;")
        unidades = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return unidades
    except Exception as e:
        return {"erro": str(e)}


# ROTA B: Gravar Unidade (Inserção de nova ou Atualização de existente)
@app.post("/api/unidades")
def salvar_unidade(dados: UnidadeSchema):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Se contiver id_unidade preenchido, o sistema processa como ATUALIZAÇÃO
        if dados.id_unidade and dados.id_unidade.strip() != "":
            # Regra de negócio: Altera apenas a descrição, convertendo para MAIÚSCULAS (.upper())
            query = "UPDATE mm_unidade SET desc_unidade = %s WHERE id_unidade = %s;"
            cursor.execute(query, (dados.desc_unidade.upper(), dados.id_unidade))
            mensagem = "Unidade atualizada com sucesso!"
        else:
            # Se não contiver id_unidade, o sistema processa como INSERÇÃO
            # Regra de negócio: Salva código e descrição em MAIÚSCULAS (.upper())
            query = "INSERT INTO mm_unidade (cod_unidade, desc_unidade) VALUES (%s, %s);"
            cursor.execute(query, (dados.cod_unidade.upper(), dados.desc_unidade.upper()))
            mensagem = "Unidade cadastrada com sucesso!"
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": mensagem}
    except Exception as e:
        return {"erro": str(e)}


# ROTA C: Excluir Unidade através do id_unidade passado na URL
@app.delete("/api/unidades/{id_unidade}")
def deletar_unidade(id_unidade: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM mm_unidade WHERE id_unidade = %s;", (id_unidade,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Unidade deletada com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}
