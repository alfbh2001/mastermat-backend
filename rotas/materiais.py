from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection # Certifique-se que o nome da sua importação de banco está correto

router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

# Modelo de dados que o frontend envia
class MaterialSchema(BaseModel):
    id_material: Optional[int] = None
    cod_material: str
    desc_material: str
    desc_completa: Optional[str] = ""
    cod_unidade: str
    cod_categoria: str
    qt_minimo: float = 0
    percent_seguranca: float = 0
    data_movto: Optional[str] = None
    usuario: Optional[str] = None

# 1. ROTA GET: Busca lista de materiais
@router.get("")
def listar_materiais():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # ou DictCursor dependendo do seu driver
        cursor.execute("SELECT * FROM materiais ORDER BY desc_material")
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. ROTA POST: Insere ou Atualiza Material (A que estava dando 404!)
@router.post("")
def salvar_material(mat: MaterialSchema):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if mat.id_material:
            # UPDATE (Edição)
            sql = """
                UPDATE materiais 
                SET cod_material=%s, desc_material=%s, desc_completa=%s, 
                    cod_unidade=%s, cod_categoria=%s, qt_minimo=%s, percent_seguranca=%s
                WHERE id_material=%s
            """
            params = (
                mat.cod_material, mat.desc_material, mat.desc_completa,
                mat.cod_unidade, mat.cod_categoria, mat.qt_minimo, 
                mat.percent_seguranca, mat.id_material
            )
            cursor.execute(sql, params)
        else:
            # INSERT (Inclusão)
            sql = """
                INSERT INTO materiais 
                (cod_material, desc_material, desc_completa, cod_unidade, cod_categoria, qt_minimo, percent_seguranca)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                mat.cod_material, mat.desc_material, mat.desc_completa,
                mat.cod_unidade, mat.cod_categoria, mat.qt_minimo, mat.percent_seguranca
            )
            cursor.execute(sql, params)

        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Material salvo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
