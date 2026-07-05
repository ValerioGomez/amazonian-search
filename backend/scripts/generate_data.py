"""
Script de generación de datos para AmazoníaSearch.

Este script procesa el CSV de atracciones y genera:
1. DataFrame serializado (data.pkl)
2. Embeddings de cada atracción (embeddings.npy)
3. Índice HNSW (hnsw_index.bin)
4. Gráficos de experimentos con diferentes parámetros

Ejecutar desde la raíz del proyecto:
    python -m backend.scripts.generate_data
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para generar gráficos
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────────────────────────────
# Configuración de logging
# ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Rutas del proyecto
# ──────────────────────────────────────────────────────────────────────
# Directorio raíz del proyecto (dos niveles arriba de este script)
RAIZ_PROYECTO: Path = Path(__file__).resolve().parent.parent.parent
# Directorio de datos del backend
DIR_DATOS_BACKEND: Path = Path(__file__).resolve().parent.parent / "data"
# CSV original en la raíz del proyecto
RUTA_CSV_ORIGINAL: Path = RAIZ_PROYECTO / "data" / "atracciones.csv"


def crear_directorio_datos() -> None:
    """Crea el directorio de datos del backend si no existe."""
    DIR_DATOS_BACKEND.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directorio de datos asegurado: {DIR_DATOS_BACKEND}")


def cargar_csv() -> pd.DataFrame:
    """
    Carga el CSV de atracciones desde la raíz del proyecto.

    Returns:
        DataFrame con los datos de las atracciones.
    """
    logger.info(f"Cargando CSV desde: {RUTA_CSV_ORIGINAL}")

    if not RUTA_CSV_ORIGINAL.exists():
        logger.error(f"No se encontró el archivo CSV: {RUTA_CSV_ORIGINAL}")
        sys.exit(1)

    df = pd.read_csv(RUTA_CSV_ORIGINAL)
    logger.info(
        f"CSV cargado — {len(df)} filas, columnas: {list(df.columns)}"
    )
    return df


def copiar_csv_a_backend() -> None:
    """Copia el CSV original al directorio de datos del backend."""
    destino = DIR_DATOS_BACKEND / "atracciones.csv"
    shutil.copy2(str(RUTA_CSV_ORIGINAL), str(destino))
    logger.info(f"CSV copiado a: {destino}")


def crear_texto_combinado(df: pd.DataFrame) -> list[str]:
    """
    Crea un campo de texto combinado para cada atracción que será
    utilizado para generar los embeddings.

    El formato es: "{nombre}. Categoría: {categoria}. {descripcion}. Ubicación: {ubicacion}."

    Args:
        df: DataFrame con las atracciones.

    Returns:
        Lista de textos combinados.
    """
    logger.info("Creando textos combinados para embeddings...")

    textos: list[str] = []
    for _, fila in df.iterrows():
        texto = (
            f"{fila['nombre']}. "
            f"Categoría: {fila['categoria']}. "
            f"{fila['descripcion']}. "
            f"Ubicación: {fila['ubicacion']}."
        )
        textos.append(texto)

    logger.info(f"Textos combinados creados — {len(textos)} textos")
    logger.info(f"Ejemplo de texto combinado:\n  → {textos[0][:150]}...")
    return textos


def generar_embeddings(textos: list[str], model_name: str) -> tuple[np.ndarray, SentenceTransformer]:
    """
    Genera embeddings para todos los textos usando SentenceTransformer.

    Args:
        textos: Lista de textos a codificar.
        model_name: Nombre del modelo a utilizar.

    Returns:
        Tupla de (embeddings, modelo) para reutilizar el modelo.
    """
    logger.info(f"Cargando modelo: {model_name}")
    inicio = time.time()
    modelo = SentenceTransformer(model_name)
    tiempo_carga = time.time() - inicio
    logger.info(f"Modelo cargado en {tiempo_carga:.2f} segundos")

    logger.info(f"Generando embeddings para {len(textos)} textos...")
    inicio = time.time()
    embeddings = modelo.encode(
        textos,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    )
    tiempo_encode = time.time() - inicio
    logger.info(
        f"Embeddings generados en {tiempo_encode:.2f} segundos — "
        f"forma: {embeddings.shape}"
    )

    return embeddings, modelo


def guardar_embeddings(embeddings: np.ndarray) -> Path:
    """
    Guarda los embeddings en un archivo .npy.

    Args:
        embeddings: Matriz de embeddings a guardar.

    Returns:
        Ruta del archivo guardado.
    """
    ruta = DIR_DATOS_BACKEND / "embeddings.npy"
    np.save(str(ruta), embeddings)
    logger.info(f"Embeddings guardados en: {ruta}")
    return ruta


def guardar_dataframe(df: pd.DataFrame) -> Path:
    """
    Guarda el DataFrame serializado en formato pickle.

    Args:
        df: DataFrame a guardar.

    Returns:
        Ruta del archivo guardado.
    """
    ruta = DIR_DATOS_BACKEND / "data.pkl"
    df.to_pickle(str(ruta))
    logger.info(f"DataFrame guardado en: {ruta}")
    return ruta


def construir_indice_hnsw(
    embeddings: np.ndarray,
    M: int = 16,
    ef_construction: int = 200,
    space: str = "cosine",
) -> "hnswlib.Index":
    """
    Construye un índice HNSW a partir de los embeddings.

    Args:
        embeddings: Matriz de embeddings.
        M: Parámetro M del grafo HNSW.
        ef_construction: Factor de calidad durante la construcción.
        space: Métrica de distancia.

    Returns:
        Índice HNSW construido.
    """
    import hnswlib

    logger.info(
        f"Construyendo índice HNSW — M={M}, ef_construction={ef_construction}, "
        f"espacio={space}"
    )
    inicio = time.time()

    num_elementos, dim = embeddings.shape
    indice = hnswlib.Index(space=space, dim=dim)
    indice.init_index(
        max_elements=num_elementos,
        M=M,
        ef_construction=ef_construction,
    )
    ids = np.arange(num_elementos)
    indice.add_items(embeddings, ids)

    tiempo_build = time.time() - inicio
    logger.info(
        f"Índice HNSW construido en {tiempo_build:.4f} segundos — "
        f"{indice.get_current_count()} elementos"
    )
    return indice


def guardar_indice_hnsw(indice: "hnswlib.Index") -> Path:
    """
    Guarda el índice HNSW en un archivo .bin.

    Args:
        indice: Índice HNSW a guardar.

    Returns:
        Ruta del archivo guardado.
    """
    ruta = DIR_DATOS_BACKEND / "hnsw_index.bin"
    indice.save_index(str(ruta))
    logger.info(f"Índice HNSW guardado en: {ruta}")
    return ruta


def calcular_vecinos_reales(
    embeddings: np.ndarray, indices_consulta: np.ndarray, k: int = 10
) -> np.ndarray:
    """
    Calcula los vecinos más cercanos reales (fuerza bruta) para
    evaluar la calidad (recall) del índice HNSW.

    Args:
        embeddings: Matriz completa de embeddings.
        indices_consulta: Índices de las consultas de prueba.
        k: Número de vecinos a encontrar.

    Returns:
        Matriz de forma (len(indices_consulta), k) con los IDs reales.
    """
    logger.info(
        f"Calculando vecinos reales por fuerza bruta para {len(indices_consulta)} consultas..."
    )
    consultas = embeddings[indices_consulta]
    # Calcular similitud coseno entre consultas y todos los embeddings
    similitudes = cosine_similarity(consultas, embeddings)

    vecinos_reales = []
    for i in range(len(indices_consulta)):
        # Ordenar por similitud descendente y tomar los top-k
        # (excluyendo el propio elemento)
        orden = np.argsort(-similitudes[i])
        # Filtrar el propio índice de la consulta
        orden = orden[orden != indices_consulta[i]]
        vecinos_reales.append(orden[:k])

    return np.array(vecinos_reales)


def calcular_recall(
    resultados_hnsw: np.ndarray, vecinos_reales: np.ndarray
) -> float:
    """
    Calcula el recall@k comparando los resultados HNSW con los reales.

    Args:
        resultados_hnsw: IDs encontrados por HNSW.
        vecinos_reales: IDs reales (fuerza bruta).

    Returns:
        Recall promedio como fracción (0 a 1).
    """
    recalls = []
    for hnsw_ids, real_ids in zip(resultados_hnsw, vecinos_reales):
        # Contar cuántos resultados de HNSW están en los reales
        comunes = len(set(hnsw_ids) & set(real_ids))
        recalls.append(comunes / len(real_ids))
    return float(np.mean(recalls))


def ejecutar_experimentos(embeddings: np.ndarray) -> dict:
    """
    Ejecuta experimentos variando el parámetro M del índice HNSW.
    Mide recall, tiempo de búsqueda y tamaño del índice.

    Args:
        embeddings: Matriz de embeddings para los experimentos.

    Returns:
        Diccionario con los resultados de los experimentos.
    """
    import hnswlib

    valores_M = [8, 16, 32, 48]
    k = 10
    num_consultas = 10
    ef_search = 50

    logger.info("=" * 60)
    logger.info("INICIANDO EXPERIMENTOS CON DIFERENTES VALORES DE M")
    logger.info("=" * 60)

    # Seleccionar consultas de prueba aleatorias
    np.random.seed(42)
    indices_consulta = np.random.choice(
        len(embeddings), size=num_consultas, replace=False
    )

    # Calcular vecinos reales por fuerza bruta
    vecinos_reales = calcular_vecinos_reales(embeddings, indices_consulta, k)

    resultados: dict = {
        "valores_M": valores_M,
        "recalls": [],
        "tiempos_busqueda": [],
        "tamaños_indice": [],
    }

    for M in valores_M:
        logger.info(f"\n--- Experimento con M={M} ---")

        # Construir índice con el valor de M actual
        indice = construir_indice_hnsw(
            embeddings, M=M, ef_construction=200, space="cosine"
        )

        # Guardar temporalmente para medir tamaño
        ruta_temp = DIR_DATOS_BACKEND / f"temp_index_M{M}.bin"
        indice.save_index(str(ruta_temp))
        tamaño_bytes = ruta_temp.stat().st_size
        tamaño_kb = tamaño_bytes / 1024
        ruta_temp.unlink()  # Eliminar archivo temporal

        # Medir tiempo de búsqueda promedio
        indice.set_ef(ef_search)
        consultas = embeddings[indices_consulta]

        tiempos = []
        todos_ids = []
        for consulta in consultas:
            inicio = time.time()
            ids, _ = indice.knn_query(consulta.reshape(1, -1), k=k)
            tiempos.append((time.time() - inicio) * 1000)  # Milisegundos
            todos_ids.append(ids[0])

        tiempo_promedio = np.mean(tiempos)
        resultados_hnsw = np.array(todos_ids)

        # Calcular recall
        recall = calcular_recall(resultados_hnsw, vecinos_reales)

        resultados["recalls"].append(recall)
        resultados["tiempos_busqueda"].append(tiempo_promedio)
        resultados["tamaños_indice"].append(tamaño_kb)

        logger.info(
            f"  M={M}: Recall@{k}={recall:.4f}, "
            f"Tiempo={tiempo_promedio:.4f} ms, "
            f"Tamaño={tamaño_kb:.1f} KB"
        )

    return resultados


def generar_grafico_experimentos(resultados: dict) -> None:
    """
    Genera el gráfico completo de experimentos (2x2 subplots).

    Args:
        resultados: Diccionario con los resultados de los experimentos.
    """
    logger.info("Generando gráfico de experimentos completos...")

    try:
        plt.style.use("seaborn-v0_8-darkgrid")
    except OSError:
        plt.style.use("ggplot")

    valores_M = resultados["valores_M"]
    recalls = resultados["recalls"]
    tiempos = resultados["tiempos_busqueda"]
    tamaños = resultados["tamaños_indice"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "AmazoníaSearch — Experimentos HNSW con Diferentes Valores de M",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    # Subplot 1: Recall vs M
    ax1 = axes[0, 0]
    ax1.plot(valores_M, recalls, "o-", color="#2E86AB", linewidth=2, markersize=8)
    ax1.set_xlabel("Parámetro M", fontsize=12)
    ax1.set_ylabel("Recall@10", fontsize=12)
    ax1.set_title("Recall vs Parámetro M", fontsize=13, fontweight="bold")
    ax1.set_xticks(valores_M)
    ax1.set_ylim([0, 1.05])
    ax1.grid(True, alpha=0.3)
    # Anotar valores
    for x, y in zip(valores_M, recalls):
        ax1.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=9,
        )

    # Subplot 2: Tiempo de búsqueda vs M
    ax2 = axes[0, 1]
    ax2.plot(valores_M, tiempos, "s-", color="#A23B72", linewidth=2, markersize=8)
    ax2.set_xlabel("Parámetro M", fontsize=12)
    ax2.set_ylabel("Tiempo de búsqueda (ms)", fontsize=12)
    ax2.set_title("Tiempo de Búsqueda vs Parámetro M", fontsize=13, fontweight="bold")
    ax2.set_xticks(valores_M)
    ax2.grid(True, alpha=0.3)
    for x, y in zip(valores_M, tiempos):
        ax2.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 12),
            ha="center",
            fontsize=9,
        )

    # Subplot 3: Recall vs Tiempo (trade-off)
    ax3 = axes[1, 0]
    ax3.plot(tiempos, recalls, "D-", color="#F18F01", linewidth=2, markersize=8)
    ax3.set_xlabel("Tiempo de búsqueda (ms)", fontsize=12)
    ax3.set_ylabel("Recall@10", fontsize=12)
    ax3.set_title("Trade-off: Recall vs Tiempo", fontsize=13, fontweight="bold")
    ax3.grid(True, alpha=0.3)
    for x, y, m in zip(tiempos, recalls, valores_M):
        ax3.annotate(
            f"M={m}",
            (x, y),
            textcoords="offset points",
            xytext=(10, 5),
            ha="left",
            fontsize=9,
        )

    # Subplot 4: Tamaño del índice vs M
    ax4 = axes[1, 1]
    ax4.bar(
        [str(m) for m in valores_M],
        tamaños,
        color=["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"],
        edgecolor="white",
        linewidth=1.5,
    )
    ax4.set_xlabel("Parámetro M", fontsize=12)
    ax4.set_ylabel("Tamaño del índice (KB)", fontsize=12)
    ax4.set_title("Tamaño del Índice vs Parámetro M", fontsize=13, fontweight="bold")
    ax4.grid(True, alpha=0.3, axis="y")
    for i, (m, t) in enumerate(zip(valores_M, tamaños)):
        ax4.text(i, t + 0.5, f"{t:.1f} KB", ha="center", fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    ruta_grafico = DIR_DATOS_BACKEND / "experimentos_completos.png"
    fig.savefig(str(ruta_grafico), dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Gráfico de experimentos guardado en: {ruta_grafico}")


def generar_grafico_informe(resultados: dict) -> None:
    """
    Genera un gráfico profesional de doble eje para el informe:
    Recall@10 y Tiempo de Búsqueda vs Parámetro M.

    Args:
        resultados: Diccionario con los resultados de los experimentos.
    """
    logger.info("Generando gráfico para informe...")

    try:
        plt.style.use("seaborn-v0_8-darkgrid")
    except OSError:
        plt.style.use("ggplot")

    valores_M = resultados["valores_M"]
    recalls = resultados["recalls"]
    tiempos = resultados["tiempos_busqueda"]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Eje izquierdo: Recall@10
    color_recall = "#2E86AB"
    ax1.set_xlabel("Parámetro M", fontsize=13)
    ax1.set_ylabel("Recall@10", fontsize=13, color=color_recall)
    linea_recall = ax1.plot(
        valores_M,
        recalls,
        "o-",
        color=color_recall,
        linewidth=2.5,
        markersize=10,
        label="Recall@10",
        zorder=5,
    )
    ax1.tick_params(axis="y", labelcolor=color_recall)
    ax1.set_xticks(valores_M)
    ax1.set_ylim([0, 1.05])

    # Anotar valores de recall
    for x, y in zip(valores_M, recalls):
        ax1.annotate(
            f"{y:.3f}",
            (x, y),
            textcoords="offset points",
            xytext=(-15, 12),
            ha="center",
            fontsize=10,
            color=color_recall,
            fontweight="bold",
        )

    # Eje derecho: Tiempo de búsqueda
    ax2 = ax1.twinx()
    color_tiempo = "#C73E1D"
    ax2.set_ylabel("Tiempo de búsqueda (ms)", fontsize=13, color=color_tiempo)
    linea_tiempo = ax2.plot(
        valores_M,
        tiempos,
        "s--",
        color=color_tiempo,
        linewidth=2.5,
        markersize=10,
        label="Tiempo de búsqueda",
        zorder=5,
    )
    ax2.tick_params(axis="y", labelcolor=color_tiempo)

    # Anotar valores de tiempo
    for x, y in zip(valores_M, tiempos):
        ax2.annotate(
            f"{y:.3f} ms",
            (x, y),
            textcoords="offset points",
            xytext=(15, -12),
            ha="center",
            fontsize=10,
            color=color_tiempo,
            fontweight="bold",
        )

    # Leyenda combinada
    lineas = linea_recall + linea_tiempo
    etiquetas = [l.get_label() for l in lineas]
    ax1.legend(lineas, etiquetas, loc="lower right", fontsize=11, framealpha=0.9)

    # Título
    fig.suptitle(
        "AmazoníaSearch — Recall@10 y Tiempo de Búsqueda vs Parámetro M",
        fontsize=15,
        fontweight="bold",
        y=1.02,
    )

    plt.tight_layout()

    ruta_grafico = DIR_DATOS_BACKEND / "grafico_informe.png"
    fig.savefig(str(ruta_grafico), dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Gráfico de informe guardado en: {ruta_grafico}")


def imprimir_resumen() -> None:
    """Imprime un resumen de todos los archivos generados con sus tamaños."""
    print("\n" + "=" * 60)
    print("  RESUMEN DE ARCHIVOS GENERADOS")
    print("=" * 60)

    archivos = [
        "atracciones.csv",
        "data.pkl",
        "embeddings.npy",
        "hnsw_index.bin",
        "experimentos_completos.png",
        "grafico_informe.png",
    ]

    for nombre in archivos:
        ruta = DIR_DATOS_BACKEND / nombre
        if ruta.exists():
            tamaño = ruta.stat().st_size
            if tamaño >= 1024 * 1024:
                tamaño_str = f"{tamaño / (1024 * 1024):.2f} MB"
            elif tamaño >= 1024:
                tamaño_str = f"{tamaño / 1024:.2f} KB"
            else:
                tamaño_str = f"{tamaño} bytes"
            print(f"  [OK]    {nombre:<30} {tamaño_str:>12}")
        else:
            print(f"  [ERROR] {nombre:<30} {'NO ENCONTRADO':>12}")

    print("=" * 60)


def main() -> None:
    """Función principal que ejecuta todo el pipeline de generación de datos."""
    print("\n" + "=" * 60)
    print("  AmazoníaSearch — Generación de Datos")
    print("=" * 60 + "\n")

    inicio_total = time.time()

    # Paso 1: Crear directorio de datos
    crear_directorio_datos()

    # Paso 2: Cargar y copiar el CSV
    df = cargar_csv()
    copiar_csv_a_backend()

    # Paso 3: Crear textos combinados para embeddings
    textos = crear_texto_combinado(df)

    # Paso 4: Generar embeddings
    nombre_modelo = "paraphrase-multilingual-MiniLM-L12-v2"
    embeddings, modelo = generar_embeddings(textos, nombre_modelo)

    # Paso 5: Guardar embeddings
    guardar_embeddings(embeddings)

    # Paso 6: Guardar DataFrame
    guardar_dataframe(df)

    # Paso 7: Construir y guardar índice HNSW
    indice = construir_indice_hnsw(embeddings, M=16, ef_construction=200)
    guardar_indice_hnsw(indice)

    # Paso 8: Ejecutar experimentos y generar gráficos
    resultados = ejecutar_experimentos(embeddings)
    generar_grafico_experimentos(resultados)
    generar_grafico_informe(resultados)

    # Paso 9: Imprimir resumen
    tiempo_total = time.time() - inicio_total
    imprimir_resumen()

    print(f"\n  Tiempo total de ejecución: {tiempo_total:.2f} segundos")
    print("  ¡Generación de datos completada exitosamente! ✓\n")


if __name__ == "__main__":
    main()
