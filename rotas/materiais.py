import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Roteador de Materiais
router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

# Função auxiliar para conectar ao banco de dados no Render
def get_db_connection():
    # Pega a URL do banco das variáveis de ambiente do Render (ex: DATABASE_URL)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("Variável DATABASE_URL não configurada no ambiente.")
    return psycopg2.connect(DATABASE_URL)

# Modelo de dados enviado pelo frontend no salvamento
class MaterialSchema(BaseModel):
    id_material: Optional[int] = None
    cod_material: str
    desc_simples: str
    desc_completa: Optional[str] = ""
    unidade: str
    categoria: str
    qt_minimo: Optional[float] = 0
    percent_seguranca: Optional[float] = 0

# 1. ROTA GET: Busca lista de materiais
@router.get("")
def listar_materiais():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM materiais ORDER BY desc_material")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar materiais: {str(e)}")

# 2. ROTA POST: Insere ou Atualiza Material
@router.post("")
def salvar_material(mat: MaterialSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if mat.id_material:
            # UPDATE (Atualização)
            sql = """
                UPDATE materiais 
                SET cod_material = %s, 
                    desc_simples = %s, 
                    desc_completa = %s, 
                    unidade = %s, 
                    categoria = %s, 
                    qt_minimo = %s, 
                    percent_seguranca = %s
                WHERE id_material = %s
            """
            params = (
                mat.cod_material, mat.desc_simples, mat.desc_completa,
                mat.unidade, mat.categoria, mat.qt_minimo, 
                mat.percent_seguranca, mat.id_material
            )
        else:
            # INSERT (Inclusão)
            sql = """
                INSERT INTO materiais 
                (cod_material, desc_simples, desc_completa, unidade, categoria, qt_minimo, percent_seguranca)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                mat.cod_material, mat.desc_simples, mat.desc_completa,
                mat.unidade, mat.categoria, mat.qt_minimo, mat.percent_seguranca
            )

        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Material salvo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar material: {str(e)}")
