import os
from datetime import date
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/projetos", tags=["Projeto"])

# Recomendado: pegar via variável de ambiente, com fallback para a string original
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"
)

class ProjetoSchema(BaseModel):
    id_projeto: Optional[int] = None
    cod_projeto: str
    nome_projeto: str
    responsavel: Optional[str] = None
    dt_criado: Optional[date] = None
    criado_por: Optional[str] = "SISTEMA"

# 1. LISTAR PROJETOS
@router.get("")
def listar_projetos():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_projeto, cod_projeto, nome_projeto, responsavel, dt_criado, criado_por FROM mm_projeto ORDER BY cod_projeto;")
        projetos = cursor.fetchall()
        cursor.close()
        conn.close()
        return projetos
    except Exception as e:
        return {"erro": str(e)}

# 2. GRAVAR OU ATUALIZAR PROJETO
@router.post("")
def salvar_projeto(dados: ProjetoSchema):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Tratamento de valores nulos/opcionais em maiúsculas
        responsavel_upper = dados.responsavel.upper() if dados.responsavel else None
        criado_por_upper = dados.criado_por.upper() if dados.criado_por else "SISTEMA"
        data_criacao = dados.dt_criado if dados.dt_criado else date.today()

        if dados.id_projeto and dados.id_projeto > 0:
            # Edição: Atualiza nome e responsável
            query = "UPDATE mm_projeto SET nome_projeto = %s, responsavel = %s WHERE id_projeto = %s;"
            cursor.execute(query, (dados.nome_projeto.upper(), responsavel_upper, dados.id_projeto))
            mensagem = "Projeto atualizado com sucesso!"
        else:
            # Inserção: Salva novo registro
            query = """
                INSERT INTO mm_projeto (cod_projeto, nome_projeto, responsavel, dt_criado, criado_por) 
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
                dados.cod_projeto.upper(), 
                dados.nome_projeto.upper(), 
                responsavel_upper, 
                data_criacao, 
                criado_por_upper
            ))
            mensagem = "Projeto cadastrado com sucesso!"
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": mensagem}
    except Exception as e:
        return {"erro": str(e)}

# 3. DELETAR PROJETO
@router.delete("/{id_projeto}")
def deletar_projeto(id_projeto: int):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mm_projeto WHERE id_projeto = %s;", (id_projeto,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Projeto deletado com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}
