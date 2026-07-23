 from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# Roteador dos materiais
router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

# URL direta de conexão com o banco Neon
DATABASE_URL = "postgresql://neondb_owner:npg_8Sh0tXnixrcv@ep-sparkling-poetry-ac0ocu3z-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Schema permissivo
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

# 1. ROTA GET: Busca lista de materiais formatada para o Grid do Frontend
@router.get("")
def listar_materiais():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM mm_material ORDER BY desc_simples")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formata o retorno para cobrir todos os nomes de campos que o Grid possa esperar
        lista_formatada = []
        for row in dados:
            item = dict(row)
            # Aliases para o Frontend/Grid
            item["desc_material"] = row.get("desc_simples") or row.get("desc_material") or ""
            item["cod_unidade"] = row.get("unidade") or row.get("cod_unidade") or ""
            item["cod_categoria"] = row.get("categoria") or row.get("cod_categoria") or ""
            lista_formatada.append(item)

        return lista_formatada
    except Exception as e:
        print("ERRO GET MATERIAIS:", str(e))
        raise HTTPException(status_code=500, detail=f"Erro ao buscar materiais: {str(e)}")

# 2. ROTA POST: Insere ou Atualiza Material
@router.post("")
def salvar_material(mat: MaterialSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mapeia aliases do frontend para os nomes reais do banco
        cod_mat = str(mat.cod_material or "")
        desc = str(mat.desc_simples or mat.desc_material or "")
        desc_comp = str(mat.desc_completa or "")
        uni = str(mat.unidade or mat.cod_unidade or "")
        cat = str(mat.categoria or mat.cod_categoria or "")
        usr = str(mat.usuario) if mat.usuario is not None else None
        
        # Formata data_movto caso venha como YYYYMMDD
        dt_mov = str(mat.data_movto) if mat.data_movto else None
        if dt_mov and len(dt_mov) == 8 and dt_mov.isdigit():
            dt_mov = f"{dt_mov[0:4]}-{dt_mov[4:6]}-{dt_mov[6:8]}"

        # Trata os números
        qt_min = float(mat.qt_minimo) if mat.qt_minimo not in (None, "") else 0.0
        perc_seg = float(mat.percent_seguranca) if mat.percent_seguranca not in (None, "") else 0.0

        if mat.id_material:
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
