import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# Roteador de Materiais
router = APIRouter(prefix="/api/materiais", tags=["Materiais"])

# Função auxiliar para conectar ao banco de dados no Render
def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("Variável DATABASE_URL não configurada no ambiente.")
    return psycopg2.connect(DATABASE_URL)

# Modelo de dados permissivo
class MaterialSchema(BaseModel):
    id_material: Optional[Any] = None
    cod_material: Optional[Any] = ""
    desc_simples: Optional[Any] = ""
    desc_material: Optional[Any] = None
    desc_completa: Optional[Any] = ""
    unidade: Optional[Any] = ""
    cod_unidade: Optional[Any] = None
    categoria: Optional[Any] = ""
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
        cursor.execute("SELECT * FROM materiais ORDER BY desc_simples")
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

        # Unifica aliases de campos caso o frontend envie nomes alternativos
        descricao = str(mat.desc_simples or mat.desc_material or "")
        uni = str(mat.unidade or mat.cod_unidade or "")
        cat = str(mat.categoria or mat.cod_categoria or "")
        
        # Conversão segura para numéricos
        qt_min = float(mat.qt_minimo) if mat.qt_minimo not in (None, "") else 0.0
        perc_seg = float(mat.percent_seguranca) if mat.percent_seguranca not in (None, "") else 0.0
        
        # Conversão de nulos/strings
        usr = str(mat.usuario) if mat.usuario is not None else None
        dt_mov = str(mat.data_movto) if mat.data_movto is not None else None

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
                str(mat.cod_material or ""), descricao, str(mat.desc_completa or ""),
                uni, cat, qt_min, perc_seg, int(mat.id_material)
            )
        else:
            # INSERT (Inclusão) - Tenta primeiro com os campos padrão
            try:
                sql = """
                    INSERT INTO materiais 
                    (cod_material, desc_simples, desc_completa, unidade, categoria, qt_minimo, percent_seguranca)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    str(mat.cod_material or ""), descricao, str(mat.desc_completa or ""),
                    uni, cat, qt_min, perc_seg
                )
                cursor.execute(sql, params)
            except Exception as insert_err:
                conn.rollback() # Limpa a transação com erro
                
                # Segunda tentativa: Tenta incluir data_movto e usuario caso o banco exija
                sql_alt = """
                    INSERT INTO materiais 
                    (cod_material, desc_simples, desc_completa, cod_unidade, cod_categoria, qt_minimo, percent_seguranca, data_movto, usuario)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_alt = (
                    str(mat.cod_material or ""), descricao, str(mat.desc_completa or ""),
                    uni, cat, qt_min, perc_seg, dt_mov, usr
                )
                cursor.execute(sql_alt, params_alt)

        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Material salvo com sucesso!"}
    except Exception as e:
        print("ERRO NO BANCO DE DADOS:", str(e))
        # Retorna o motivo exato do banco de dados na resposta para identificarmos na hora
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")
