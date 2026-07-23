from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/projeto", tags=["Projeto"])

DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

class ProjetoSchema(BaseModel):
    id_projeto: Optional[str] = None
    cod_projeto: str
    nome_projeto: str
    responsavel: str
    dt_criado: dtt
    criado_por: str

# 1. LISTAR CATEGORIAS
@router.get("")
def listar_categorias():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_projeto, cod_projeto, nome_projeto, responsavel, dt_criado, criado_por FROM mm_projeto ORDER BY cod_projeto;")
        projeto = cursor.fetchall()
        cursor.close()
        conn.close()
        return projeto
    except Exception as e:
        return {"erro": str(e)}

# 2. GRAVAR OU ATUALIZAR CATEGORIA
@router.post("")
def salvar_projeto(dados: ProjetoSchema):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        if dados.id_projeto and dados.id_projeto.strip() != "":
            # Edição: Altera apenas a descrição em Maiúsculas
            query = "UPDATE mm_projeto SET nome_projeto = %s,  responsavel = %s WHERE id_projeto = %s;"
            cursor.execute(query, (dados.nome_projeto.upper(), ados.responsavel.upper(), dados.id_projeto))
            mensagem = "Projeto atualizado com sucesso!"
        else:
            # Inserção: Salva código e descrição em Maiúsculas
            query = "INSERT INTO mm_projeto (cod_projeto, nome_projeto, responsavel, dt_criado, criado_por ) VALUES (%s, %s, %s, %s, %s);"
            cursor.execute(query, (dados.cod_projeto.upper(), dados.nome_projeto.upper(), dados.responsavel.upper(), dados.criado_por.upper()))
            mensagem = "Projeto cadastrado com sucesso!"
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": mensagem}
    except Exception as e:
        return {"erro": str(e)}

# 3. DELETAR CATEGORIA
@router.delete("/{id_categoria}")
def deletar_categoria(id_categoria: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mm_Projeto WHERE id_Projeto = %s;", (id_projeto,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Projeto deletado com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}
