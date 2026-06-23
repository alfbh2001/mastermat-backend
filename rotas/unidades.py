from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Criamos o roteador das unidades
router = APIRouter(prefix="/api/unidades", tags=["Unidades"])

DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

class UnidadeSchema(BaseModel):
    id_unidade: Optional[str] = None
    cod_unidade: str
    desc_unidade: str

@router.get("") # Mapeia para GET /api/unidades
def listar_unidades():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_unidade, cod_unidade, desc_unidade FROM mm_unidade ORDER BY cod_unidade;")
        unidades = cursor.fetchall()
        cursor.close()
        conn.close()
        return unidades
    except Exception as e:
        return {"erro": str(e)}

@router.post("") # Mapeia para POST /api/unidades
def salvar_unidade(dados: UnidadeSchema):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        if dados.id_unidade and dados.id_unidade.strip() != "":
            query = "UPDATE mm_unidade SET desc_unidade = %s WHERE id_unidade = %s;"
            cursor.execute(query, (dados.desc_unidade.upper(), dados.id_unidade))
            mensagem = "Unidade atualizada com sucesso!"
        else:
            query = "INSERT INTO mm_unidade (cod_unidade, desc_unidade) VALUES (%s, %s);"
            cursor.execute(query, (dados.cod_unidade.upper(), dados.desc_unidade.upper()))
            mensagem = "Unidade cadastrada com sucesso!"
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": mensagem}
    except Exception as e:
        return {"erro": str(e)}

@router.delete("/{id_unidade}") # Mapeia para DELETE /api/unidades/{id_unidade}
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
