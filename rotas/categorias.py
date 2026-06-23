from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])

DATABASE_URL = "SUA_URL_DO_NEON_AQUI"

class CategoriaSchema(BaseModel):
    id_categoria: Optional[str] = None
    cod_categoria: str
    desc_categoria: str

# 1. LISTAR CATEGORIAS
@router.get("")
def listar_categorias():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_categoria, cod_categoria, desc_categoria FROM mm_categoria ORDER BY cod_categoria;")
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return categorias
    except Exception as e:
        return {"erro": str(e)}

# 2. GRAVAR OU ATUALIZAR CATEGORIA
@router.post("")
def salvar_categoria(dados: CategoriaSchema):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        if dados.id_categoria and dados.id_categoria.strip() != "":
            # Edição: Altera apenas a descrição em Maiúsculas
            query = "UPDATE mm_categoria SET desc_categoria = %s WHERE id_categoria = %s;"
            cursor.execute(query, (dados.desc_categoria.upper(), dados.id_categoria))
            mensagem = "Categoria atualizada com sucesso!"
        else:
            # Inserção: Salva código e descrição em Maiúsculas
            query = "INSERT INTO mm_categoria (cod_categoria, desc_categoria) VALUES (%s, %s);"
            cursor.execute(query, (dados.cod_categoria.upper(), dados.desc_categoria.upper()))
            mensagem = "Categoria cadastrada com sucesso!"
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": mensaje || mensagem}
    except Exception as e:
        return {"erro": str(e)}

# 3. DELETAR CATEGORIA
@router.delete("/{id_categoria}")
def deletar_categoria(id_categoria: str):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mm_categoria WHERE id_categoria = %s;", (id_categoria,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"sucesso": True, "mensagem": "Categoria deletada com sucesso!"}
    except Exception as e:
        return {"erro": str(e)}
