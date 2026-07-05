"""
Aplicación principal FastAPI de AmazoníaSearch.

Motor de búsqueda semántica para atracciones turísticas en la
Amazonía peruana, utilizando embeddings y búsqueda HNSW.
"""

import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.api.embedding_engine import EmbeddingEngine
from backend.api.hnsw_engine import HNSWEngine

# ──────────────────────────────────────────────────────────────────────
# Configuración de logging
# ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Cargar variables de entorno desde el archivo .env del backend
# ──────────────────────────────────────────────────────────────────────
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import os

MODEL_NAME: str = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
HNSW_M: int = int(os.getenv("HNSW_M", "16"))
HNSW_EF_CONSTRUCTION: int = int(os.getenv("HNSW_EF_CONSTRUCTION", "200"))
HNSW_EF_SEARCH: int = int(os.getenv("HNSW_EF_SEARCH", "50"))
EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "384"))
HNSW_SPACE: str = os.getenv("HNSW_SPACE", "cosine")

# ──────────────────────────────────────────────────────────────────────
# Rutas a los archivos de datos
# ──────────────────────────────────────────────────────────────────────
DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
RUTA_DATAFRAME: Path = DATA_DIR / "data.pkl"
RUTA_INDICE: Path = DATA_DIR / "hnsw_index.bin"
RUTA_EMBEDDINGS: Path = DATA_DIR / "embeddings.npy"

# ──────────────────────────────────────────────────────────────────────
# Estado global de la aplicación
# ──────────────────────────────────────────────────────────────────────
motor_embeddings: EmbeddingEngine | None = None
motor_hnsw: HNSWEngine | None = None
df_atracciones: pd.DataFrame | None = None
embeddings_ref: np.ndarray | None = None


# ──────────────────────────────────────────────────────────────────────
# Modelos Pydantic para solicitudes y respuestas
# ──────────────────────────────────────────────────────────────────────
class ConsultaBusqueda(BaseModel):
    """Modelo de solicitud para el endpoint de búsqueda semántica."""

    query: str = Field(
        ...,
        description="Texto de la consulta de búsqueda",
        min_length=1,
        max_length=500,
    )
    k: int = Field(
        default=5,
        description="Número de resultados a devolver",
        ge=1,
        le=50,
    )
    categoria: str | None = Field(
        default=None,
        description="Filtro opcional por categoría de atracción",
    )


class ResultadoAtraccion(BaseModel):
    """Modelo de un resultado individual de búsqueda."""

    id: int
    nombre: str
    categoria: str
    descripcion: str
    ubicacion: str
    latitud: float
    longitud: float
    similitud: float = Field(
        description="Porcentaje de similitud con la consulta (0-100)"
    )


class RespuestaBusqueda(BaseModel):
    """Modelo de respuesta completa del endpoint de búsqueda."""

    query: str
    resultados: list[ResultadoAtraccion]
    total_resultados: int
    tiempo_busqueda_ms: float
    modelo: str
    parametros_hnsw: dict


# ──────────────────────────────────────────────────────────────────────
# Lifespan: carga de recursos al iniciar la aplicación
# ──────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Contexto de vida de la aplicación.
    Carga todos los recursos necesarios al inicio y los libera al cierre.
    """
    global motor_embeddings, motor_hnsw, df_atracciones, embeddings_ref

    logger.info("=" * 60)
    logger.info("Iniciando AmazoníaSearch — cargando recursos...")
    logger.info("=" * 60)

    try:
        # 1. Cargar el DataFrame con los datos de atracciones
        logger.info(f"Cargando DataFrame desde: {RUTA_DATAFRAME}")
        if not RUTA_DATAFRAME.exists():
            logger.error(f"Archivo no encontrado: {RUTA_DATAFRAME}")
            raise FileNotFoundError(
                f"No se encontró el archivo de datos: {RUTA_DATAFRAME}. "
                "Ejecute primero: python -m backend.scripts.generate_data"
            )
        df_atracciones = pd.read_pickle(RUTA_DATAFRAME)
        logger.info(
            f"DataFrame cargado — {len(df_atracciones)} atracciones, "
            f"columnas: {list(df_atracciones.columns)}"
        )

        # 2. Cargar el índice HNSW
        logger.info(f"Cargando índice HNSW desde: {RUTA_INDICE}")
        if not RUTA_INDICE.exists():
            logger.error(f"Archivo no encontrado: {RUTA_INDICE}")
            raise FileNotFoundError(
                f"No se encontró el índice HNSW: {RUTA_INDICE}. "
                "Ejecute primero: python -m backend.scripts.generate_data"
            )
        motor_hnsw = HNSWEngine(dim=EMBEDDING_DIM, space=HNSW_SPACE)
        motor_hnsw.load_index(
            path=str(RUTA_INDICE),
            max_elements=len(df_atracciones),
        )

        # 3. Cargar el modelo de embeddings
        logger.info(f"Cargando modelo de embeddings: {MODEL_NAME}")
        motor_embeddings = EmbeddingEngine(model_name=MODEL_NAME)

        # 4. Cargar los embeddings de referencia
        logger.info(f"Cargando embeddings desde: {RUTA_EMBEDDINGS}")
        if RUTA_EMBEDDINGS.exists():
            embeddings_ref = np.load(str(RUTA_EMBEDDINGS))
            logger.info(
                f"Embeddings cargados — forma: {embeddings_ref.shape}"
            )
        else:
            logger.warning(
                f"Archivo de embeddings no encontrado: {RUTA_EMBEDDINGS}. "
                "Continuando sin embeddings de referencia."
            )

        logger.info("=" * 60)
        logger.info("AmazoníaSearch iniciado correctamente ✓")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error al iniciar AmazoníaSearch: {e}")
        raise

    # Ceder el control a la aplicación
    yield

    # Limpieza al cerrar la aplicación
    logger.info("Cerrando AmazoníaSearch — liberando recursos...")
    motor_embeddings = None
    motor_hnsw = None
    df_atracciones = None
    embeddings_ref = None
    logger.info("Recursos liberados correctamente")


# ──────────────────────────────────────────────────────────────────────
# Creación de la aplicación FastAPI
# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AmazoníaSearch API",
    description=(
        "Motor de búsqueda semántica para atracciones turísticas "
        "en la Amazonía peruana. Utiliza embeddings multilingües y "
        "búsqueda HNSW para encontrar las atracciones más relevantes."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS para permitir todos los orígenes (desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────
# Endpoints de la API
# ──────────────────────────────────────────────────────────────────────


@app.get("/", tags=["Sistema"])
async def raiz() -> dict:
    """
    Retorna información general del sistema AmazoníaSearch.
    """
    num_atracciones = len(df_atracciones) if df_atracciones is not None else 0

    # Obtener parámetros del índice HNSW
    parametros_hnsw = motor_hnsw.get_info() if motor_hnsw else {}

    return {
        "proyecto": "AmazoníaSearch",
        "descripcion": (
            "Motor de búsqueda semántica para atracciones turísticas "
            "en la Amazonía peruana"
        ),
        "version": "1.0.0",
        "modelo": MODEL_NAME,
        "num_atracciones": num_atracciones,
        "parametros_hnsw": parametros_hnsw,
    }


@app.get("/health", tags=["Sistema"])
async def salud() -> dict:
    """
    Verifica el estado de salud del sistema.
    Retorna el estado de cada componente cargado.
    """
    return {
        "status": "ok",
        "modelo_cargado": motor_embeddings is not None,
        "indice_cargado": motor_hnsw is not None and motor_hnsw.index is not None,
        "datos_cargados": df_atracciones is not None,
    }


@app.get("/attractions", tags=["Atracciones"])
async def listar_atracciones(
    categoria: str | None = Query(
        default=None,
        description="Filtrar por categoría de atracción",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Número máximo de resultados por página",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Desplazamiento para paginación",
    ),
) -> dict:
    """
    Retorna una lista paginada de atracciones turísticas.
    Permite filtrar opcionalmente por categoría.
    """
    if df_atracciones is None:
        raise HTTPException(
            status_code=503,
            detail="Los datos de atracciones no están disponibles. "
            "El sistema aún se está iniciando.",
        )

    # Aplicar filtro de categoría si se especifica
    df_filtrado = df_atracciones.copy()
    if categoria:
        df_filtrado = df_filtrado[
            df_filtrado["categoria"].str.lower() == categoria.lower()
        ]

    total = len(df_filtrado)

    # Aplicar paginación
    df_pagina = df_filtrado.iloc[offset : offset + limit]

    # Convertir a lista de diccionarios
    atracciones = df_pagina[
        ["id", "nombre", "categoria", "descripcion", "ubicacion", "latitud", "longitud"]
    ].to_dict(orient="records")

    logger.info(
        f"Listado de atracciones — categoría: {categoria}, "
        f"offset: {offset}, limit: {limit}, total: {total}"
    )

    return {
        "atracciones": atracciones,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/attractions/{attraction_id}", tags=["Atracciones"])
async def obtener_atraccion(attraction_id: int) -> dict:
    """
    Retorna el detalle completo de una atracción por su ID.
    Lanza un error 404 si la atracción no existe.
    """
    if df_atracciones is None:
        raise HTTPException(
            status_code=503,
            detail="Los datos de atracciones no están disponibles.",
        )

    # Buscar la atracción por su columna 'id'
    fila = df_atracciones[df_atracciones["id"] == attraction_id]

    if fila.empty:
        logger.warning(f"Atracción no encontrada con ID: {attraction_id}")
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró ninguna atracción con el ID {attraction_id}.",
        )

    # Convertir la fila a diccionario
    atraccion = fila.iloc[0][
        ["id", "nombre", "categoria", "descripcion", "ubicacion", "latitud", "longitud"]
    ].to_dict()

    logger.info(f"Detalle de atracción solicitado — ID: {attraction_id}")

    return {"atraccion": atraccion}


@app.post("/search", tags=["Búsqueda"])
async def buscar(consulta: ConsultaBusqueda) -> RespuestaBusqueda:
    """
    Realiza una búsqueda semántica de atracciones turísticas.

    Proceso:
    1. Codifica la consulta en un vector de embeddings.
    2. Busca los vecinos más cercanos en el índice HNSW.
    3. Mapea los IDs a los datos completos de cada atracción.
    4. Calcula el porcentaje de similitud.
    5. Aplica filtro de categoría si se especifica.
    """
    # Validar que los componentes estén cargados
    if motor_embeddings is None:
        raise HTTPException(
            status_code=503,
            detail="El modelo de embeddings no está cargado.",
        )
    if motor_hnsw is None or motor_hnsw.index is None:
        raise HTTPException(
            status_code=503,
            detail="El índice HNSW no está cargado.",
        )
    if df_atracciones is None:
        raise HTTPException(
            status_code=503,
            detail="Los datos de atracciones no están disponibles.",
        )

    inicio = time.time()

    logger.info(
        f"Búsqueda semántica — consulta: '{consulta.query}', "
        f"k={consulta.k}, categoría: {consulta.categoria}"
    )

    # Paso 1: Codificar la consulta en un vector
    vector_consulta = motor_embeddings.encode(consulta.query)

    # Paso 2: Buscar en el índice HNSW
    # Si hay filtro de categoría, buscar más resultados para compensar el filtrado
    k_busqueda = consulta.k * 3 if consulta.categoria else consulta.k
    # No buscar más de lo que hay en el índice
    k_busqueda = min(k_busqueda, len(df_atracciones))

    ids, distancias = motor_hnsw.search(
        query_vector=vector_consulta,
        k=k_busqueda,
        ef_search=HNSW_EF_SEARCH,
    )

    # Paso 3 y 4: Mapear IDs a datos y calcular similitud
    resultados: list[ResultadoAtraccion] = []

    for idx, distancia in zip(ids, distancias):
        # Verificar que el ID existe en el DataFrame
        if idx < 0 or idx >= len(df_atracciones):
            logger.warning(f"ID fuera de rango: {idx}")
            continue

        fila = df_atracciones.iloc[idx]

        # Calcular porcentaje de similitud: (1 - distancia) * 100
        similitud = (1.0 - distancia) * 100.0
        # Asegurar que el valor está en el rango [0, 100]
        similitud = max(0.0, min(100.0, similitud))

        resultado = ResultadoAtraccion(
            id=int(fila["id"]),
            nombre=str(fila["nombre"]),
            categoria=str(fila["categoria"]),
            descripcion=str(fila["descripcion"]),
            ubicacion=str(fila["ubicacion"]),
            latitud=float(fila["latitud"]),
            longitud=float(fila["longitud"]),
            similitud=round(similitud, 2),
        )
        resultados.append(resultado)

    # Paso 5: Aplicar filtro de categoría si se especificó
    if consulta.categoria:
        resultados = [
            r
            for r in resultados
            if r.categoria.lower() == consulta.categoria.lower()
        ]

    # Limitar al número de resultados solicitados
    resultados = resultados[: consulta.k]

    # Calcular tiempo total de búsqueda
    tiempo_busqueda_ms = (time.time() - inicio) * 1000

    # Obtener parámetros HNSW para la respuesta
    parametros_hnsw = motor_hnsw.get_info()
    parametros_hnsw["ef_search"] = HNSW_EF_SEARCH

    logger.info(
        f"Búsqueda completada — {len(resultados)} resultados en "
        f"{tiempo_busqueda_ms:.2f} ms"
    )

    return RespuestaBusqueda(
        query=consulta.query,
        resultados=resultados,
        total_resultados=len(resultados),
        tiempo_busqueda_ms=round(tiempo_busqueda_ms, 2),
        modelo=MODEL_NAME,
        parametros_hnsw=parametros_hnsw,
    )


@app.get("/categories", tags=["Atracciones"])
async def listar_categorias() -> dict:
    """
    Retorna la lista de categorías únicas de atracciones disponibles.
    """
    if df_atracciones is None:
        raise HTTPException(
            status_code=503,
            detail="Los datos de atracciones no están disponibles.",
        )

    # Obtener categorías únicas y ordenarlas
    categorias = sorted(df_atracciones["categoria"].unique().tolist())

    logger.info(f"Categorías consultadas — {len(categorias)} categorías únicas")

    return {
        "categorias": categorias,
        "total": len(categorias),
    }
