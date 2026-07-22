import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

def get_db_connection():
    # Tenta buscar DATABASE_URL ou variações comuns no Render
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_PUBLIC_URL")
    if not DATABASE_URL:
        raise Exception("Variável DATABASE_URL não configurada no ambiente da Render.")
    return psycopg2.connect(DATABASE_URL)

class MaterialSchema(BaseModel):
    id_material: Optional[Any] = None
    cod_material: Optional[Any] = ""
    desc_simples: Optional[Any] = None
    desc_material: Optional[Any] = None
    desc_completa: Optional[Any] = ""
    unidade: Optional[Any] = None
    cod_unidade: Optional[Any] = None
    categoria: Optional[Any] = None
    cod_categoria: Optional[Any] = None
    qt_minimo: Optional[Any] = 0
    percent_seguranca: Optional[Any] = 0
    data_movto: Optional[Any] = None
    usuario: Optional[Any] = None

# 1. ROTA GET: Busca lista de materiais da tabela mm_material
@router.get("")
def listar_materiais():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM mm_material ORDER BY desc_simples")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar materiais: {str(e)}")

# 2. ROTA POST: Insere ou Atualiza Material na tabela mm_material
@router.post("")
def salvar_material(mat: MaterialSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Alinha os nomes enviados pelo frontend aos nomes das colunas
        cod_mat = str(mat.cod_material or "")
        desc = str(mat.desc_simples or mat.desc_material or "")
        desc_comp = str(mat.desc_completa or "")
        uni = str(mat.unidade or mat.cod_unidade or "")
        cat = str(mat.categoria or mat.cod_categoria or "")
        usr = str(mat.usuario) if mat.usuario is not None else None
        
        # Formata data_movto para YYYY-MM-DD caso venha no formato YYYYMMDD
        dt_mov = str(mat.data_movto) if mat.data_movto else None
        if dt_mov and len(dt_mov) == 8 and dt_mov.isdigit():
            dt_mov = f"{dt_mov[0:4]}-{dt_mov[4:6]}-{dt_mov[6:8]}"

        # Trata os valores numéricos
        qt_min = float(mat.qt_minimo) if mat.qt_minimo not in (None, "") else 0.0
        perc_seg = float(mat.percent_seguranca) if mat.percent_seguranca not in (None, "") else 0.0

        if mat.id_material:
            # UPDATE na tabela mm_material
            sql = """
                UPDATE mm_material 
                SET cod_material = %s, 
                    desc_simples = %s, 
                    desc_completa = %s, 
                    unidade = %s, 
                    categoria = %s, 
                    usuario = %s,
                    data_movto = %s,
                    qt_minimo = %s, 
                    percent_seguranca = %s
                WHERE id_material = %s
            """
            params = (
                cod_mat, desc, desc_comp, uni, cat, 
                usr, dt_mov, qt_min, perc_seg, int(mat.id_material)
            )
        else:
            # INSERT na tabela mm_material
            sql = """
                INSERT INTO mm_material 
                (cod_material, desc_simples, desc_completa, unidade, categoria, usuario, data_movto, qt_minimo, percent_seguranca)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                cod_mat, desc, desc_comp, uni, cat, 
                usr, dt_mov, qt_min, perc_seg
            )

        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Material salvo com sucesso!"}
    except Exception as e:
        print("ERRO BANCO DE DADOS:", str(e))
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")
