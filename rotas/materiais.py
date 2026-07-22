from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# Criamos o roteador dos materiais
router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

# URL direta de conexão com o banco Neon (igual ao unidades.py)
DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Schema permissivo para aceitar nulls do frontend sem dar erro 422
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

# 1. ROTA GET: Busca lista de materiais
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

        # Mapeia aliases enviados pelo frontend para os nomes reais da tabela mm_material
        cod_mat = str(mat.cod_material or "")
        desc = str(mat.desc_simples or mat.desc_material or "")
        desc_comp = str(mat.desc_completa or "")
        uni = str(mat.unidade or mat.cod_unidade or "")
        cat = str(mat.categoria or mat.cod_categoria or "")
        usr = str(mat.usuario) if mat.usuario is not None else None
        
        # Formata data_movto caso venha como YYYYMMDD do frontend
        dt_mov = str(mat.data_movto) if mat.data_movto else None
        if dt_mov and len(dt_mov) == 8 and dt_mov.isdigit():
            dt_mov = f"{dt_mov[0:4]}-{dt_mov[4:6]}-{dt_mov[6:8]}"

        # Trata os números
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
