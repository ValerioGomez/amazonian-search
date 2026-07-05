"""
Script de benchmark para AmazoníaSearch.

Evalúa el rendimiento del índice HNSW con diferentes combinaciones
de parámetros M y ef_search, midiendo:
- Tiempo de construcción del índice
- Tiempo promedio de búsqueda
- Recall@10

Ejecutar desde la raíz del proyecto:
    python -m backend.scripts.benchmark
"""

import time
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo
import matplotlib.pyplot as plt
import hnswlib
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────────────────────────────
# Colores ANSI
# ──────────────────────────────────────────────────────────────────────
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CIAN = "\033[96m"
NEGRITA = "\033[1m"
RESET = "\033[0m"

# ──────────────────────────────────────────────────────────────────────
# Rutas de datos
# ──────────────────────────────────────────────────────────────────────
DIR_DATOS: Path = Path(__file__).resolve().parent.parent / "data"
RUTA_EMBEDDINGS: Path = DIR_DATOS / "embeddings.npy"
RUTA_DATAFRAME: Path = DIR_DATOS / "data.pkl"

# ──────────────────────────────────────────────────────────────────────
# Parámetros del benchmark
# ──────────────────────────────────────────────────────────────────────
VALORES_M: list[int] = [8, 16, 32, 48]
VALORES_EF_SEARCH: list[int] = [10, 20, 50, 100, 200]
EF_CONSTRUCTION: int = 200
K: int = 10
NUM_CONSULTAS: int = 50
DIM: int = 384
SPACE: str = "cosine"


def cargar_datos() -> tuple[np.ndarray, pd.DataFrame]:
    """
    Carga los embeddings y el DataFrame de atracciones.

    Returns:
        Tupla de (embeddings, DataFrame).
    """
    print(f"\n{NEGRITA}Cargando datos...{RESET}")

    if not RUTA_EMBEDDINGS.exists():
        print(f"{ROJO}Error: No se encontró {RUTA_EMBEDDINGS}{RESET}")
        print(f"Ejecute primero: python -m backend.scripts.generate_data")
        sys.exit(1)

    if not RUTA_DATAFRAME.exists():
        print(f"{ROJO}Error: No se encontró {RUTA_DATAFRAME}{RESET}")
        sys.exit(1)

    embeddings = np.load(str(RUTA_EMBEDDINGS))
    df = pd.read_pickle(str(RUTA_DATAFRAME))

    print(f"  Embeddings cargados: {embeddings.shape}")
    print(f"  DataFrame cargado: {len(df)} filas")

    return embeddings, df


def calcular_ground_truth(
    embeddings: np.ndarray, indices_consulta: np.ndarray, k: int
) -> np.ndarray:
    """
    Calcula los vecinos más cercanos reales usando fuerza bruta
    (similitud coseno exacta).

    Args:
        embeddings: Matriz completa de embeddings.
        indices_consulta: Índices de los vectores de consulta.
        k: Número de vecinos a encontrar.

    Returns:
        Matriz de vecinos reales de forma (num_consultas, k).
    """
    print(f"  Calculando ground truth por fuerza bruta ({len(indices_consulta)} consultas)...")

    consultas = embeddings[indices_consulta]
    similitudes = cosine_similarity(consultas, embeddings)

    ground_truth = []
    for i, idx in enumerate(indices_consulta):
        # Excluir el propio vector de consulta
        similitudes[i, idx] = -1
        # Obtener los top-k más similares
        top_k = np.argsort(-similitudes[i])[:k]
        ground_truth.append(top_k)

    return np.array(ground_truth)


def calcular_recall(
    resultados_hnsw: np.ndarray, ground_truth: np.ndarray
) -> float:
    """
    Calcula el recall@k entre los resultados HNSW y los ground truth.

    Args:
        resultados_hnsw: IDs encontrados por HNSW (num_consultas, k).
        ground_truth: IDs reales (num_consultas, k).

    Returns:
        Recall promedio (0 a 1).
    """
    recalls = []
    for hnsw_ids, real_ids in zip(resultados_hnsw, ground_truth):
        comunes = len(set(hnsw_ids.tolist()) & set(real_ids.tolist()))
        recalls.append(comunes / len(real_ids))
    return float(np.mean(recalls))


def ejecutar_benchmark(
    embeddings: np.ndarray,
) -> list[dict]:
    """
    Ejecuta el benchmark con todas las combinaciones de parámetros.

    Args:
        embeddings: Matriz de embeddings.

    Returns:
        Lista de diccionarios con los resultados de cada combinación.
    """
    print(f"\n{NEGRITA}Ejecutando benchmark...{RESET}")
    print(f"  Parámetros M: {VALORES_M}")
    print(f"  Parámetros ef_search: {VALORES_EF_SEARCH}")
    print(f"  Consultas por prueba: {NUM_CONSULTAS}")
    print(f"  K (vecinos): {K}")

    # Seleccionar consultas de prueba
    np.random.seed(42)
    num_total = embeddings.shape[0]
    indices_consulta = np.random.choice(
        num_total, size=min(NUM_CONSULTAS, num_total), replace=False
    )

    # Calcular ground truth
    ground_truth = calcular_ground_truth(embeddings, indices_consulta, K)

    resultados: list[dict] = []
    total_combinaciones = len(VALORES_M) * len(VALORES_EF_SEARCH)
    combinacion_actual = 0

    for M in VALORES_M:
        # Construir el índice con este valor de M
        print(f"\n  {AZUL}Construyendo índice con M={M}...{RESET}")
        inicio_build = time.time()

        indice = hnswlib.Index(space=SPACE, dim=DIM)
        indice.init_index(
            max_elements=num_total,
            M=M,
            ef_construction=EF_CONSTRUCTION,
        )
        ids = np.arange(num_total)
        indice.add_items(embeddings, ids)

        tiempo_build = time.time() - inicio_build
        print(f"    Índice construido en {tiempo_build:.4f} s")

        for ef_search in VALORES_EF_SEARCH:
            combinacion_actual += 1
            print(
                f"    [{combinacion_actual}/{total_combinaciones}] "
                f"M={M}, ef_search={ef_search}...",
                end=" ",
            )

            # Configurar ef_search
            indice.set_ef(ef_search)

            # Medir tiempo de búsqueda
            consultas = embeddings[indices_consulta]
            tiempos: list[float] = []
            todos_ids = []

            for consulta in consultas:
                inicio = time.time()
                res_ids, _ = indice.knn_query(consulta.reshape(1, -1), k=K)
                tiempos.append((time.time() - inicio) * 1000)  # ms
                todos_ids.append(res_ids[0])

            tiempo_promedio = float(np.mean(tiempos))
            resultados_array = np.array(todos_ids)

            # Calcular recall
            recall = calcular_recall(resultados_array, ground_truth)

            resultado = {
                "M": M,
                "ef_search": ef_search,
                "ef_construction": EF_CONSTRUCTION,
                "tiempo_build_s": round(tiempo_build, 4),
                "tiempo_busqueda_ms": round(tiempo_promedio, 4),
                "recall_at_10": round(recall, 4),
            }
            resultados.append(resultado)

            # Indicador visual de recall
            if recall >= 0.95:
                color = VERDE
            elif recall >= 0.80:
                color = AMARILLO
            else:
                color = ROJO

            print(
                f"{color}Recall@10={recall:.4f}{RESET}, "
                f"Tiempo={tiempo_promedio:.4f} ms"
            )

    return resultados


def imprimir_tabla(resultados: list[dict]) -> None:
    """
    Imprime los resultados del benchmark en una tabla formateada.

    Args:
        resultados: Lista de diccionarios con los resultados.
    """
    print(f"\n{'=' * 80}")
    print(f"  {NEGRITA}RESULTADOS DEL BENCHMARK{RESET}")
    print(f"{'=' * 80}")

    # Encabezados
    print(
        f"  {'M':>4} | {'ef_search':>10} | {'ef_const':>9} | "
        f"{'Build (s)':>10} | {'Búsqueda (ms)':>14} | {'Recall@10':>10}"
    )
    print(f"  {'-' * 4}-+-{'-' * 10}-+-{'-' * 9}-+-{'-' * 10}-+-{'-' * 14}-+-{'-' * 10}")

    m_actual = None
    for r in resultados:
        # Separador visual entre diferentes valores de M
        if r["M"] != m_actual:
            if m_actual is not None:
                print(
                    f"  {'-' * 4}-+-{'-' * 10}-+-{'-' * 9}-+-"
                    f"{'-' * 10}-+-{'-' * 14}-+-{'-' * 10}"
                )
            m_actual = r["M"]

        # Color según recall
        recall = r["recall_at_10"]
        if recall >= 0.95:
            color = VERDE
        elif recall >= 0.80:
            color = AMARILLO
        else:
            color = ROJO

        print(
            f"  {r['M']:>4} | {r['ef_search']:>10} | {r['ef_construction']:>9} | "
            f"{r['tiempo_build_s']:>10.4f} | {r['tiempo_busqueda_ms']:>14.4f} | "
            f"{color}{r['recall_at_10']:>10.4f}{RESET}"
        )

    print(f"{'=' * 80}")


def generar_grafico_benchmark(resultados: list[dict]) -> None:
    """
    Genera un gráfico resumen del benchmark.

    Args:
        resultados: Lista de diccionarios con los resultados.
    """
    print(f"\n{NEGRITA}Generando gráfico de benchmark...{RESET}")

    try:
        plt.style.use("seaborn-v0_8-darkgrid")
    except OSError:
        plt.style.use("ggplot")

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        "AmazoníaSearch — Benchmark HNSW: M vs ef_search",
        fontsize=16,
        fontweight="bold",
    )

    # Colores para cada valor de M
    colores = {8: "#2E86AB", 16: "#A23B72", 32: "#F18F01", 48: "#C73E1D"}
    marcadores = {8: "o", 16: "s", 32: "D", 48: "^"}

    # Gráfico 1: Recall vs ef_search para cada M
    ax1 = axes[0]
    for M in VALORES_M:
        datos_m = [r for r in resultados if r["M"] == M]
        ef_values = [r["ef_search"] for r in datos_m]
        recalls = [r["recall_at_10"] for r in datos_m]
        ax1.plot(
            ef_values, recalls,
            f"{marcadores[M]}-",
            color=colores[M],
            label=f"M={M}",
            linewidth=2,
            markersize=8,
        )
    ax1.set_xlabel("ef_search", fontsize=12)
    ax1.set_ylabel("Recall@10", fontsize=12)
    ax1.set_title("Recall@10 vs ef_search", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.05])

    # Gráfico 2: Tiempo de búsqueda vs ef_search para cada M
    ax2 = axes[1]
    for M in VALORES_M:
        datos_m = [r for r in resultados if r["M"] == M]
        ef_values = [r["ef_search"] for r in datos_m]
        tiempos = [r["tiempo_busqueda_ms"] for r in datos_m]
        ax2.plot(
            ef_values, tiempos,
            f"{marcadores[M]}-",
            color=colores[M],
            label=f"M={M}",
            linewidth=2,
            markersize=8,
        )
    ax2.set_xlabel("ef_search", fontsize=12)
    ax2.set_ylabel("Tiempo de búsqueda (ms)", fontsize=12)
    ax2.set_title("Tiempo vs ef_search", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    # Gráfico 3: Trade-off Recall vs Tiempo
    ax3 = axes[2]
    for M in VALORES_M:
        datos_m = [r for r in resultados if r["M"] == M]
        tiempos = [r["tiempo_busqueda_ms"] for r in datos_m]
        recalls = [r["recall_at_10"] for r in datos_m]
        ax3.plot(
            tiempos, recalls,
            f"{marcadores[M]}-",
            color=colores[M],
            label=f"M={M}",
            linewidth=2,
            markersize=8,
        )
    ax3.set_xlabel("Tiempo de búsqueda (ms)", fontsize=12)
    ax3.set_ylabel("Recall@10", fontsize=12)
    ax3.set_title("Trade-off: Recall vs Tiempo", fontsize=13, fontweight="bold")
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([0, 1.05])

    plt.tight_layout(rect=[0, 0, 1, 0.93])

    ruta_grafico = DIR_DATOS / "benchmark_results.png"
    fig.savefig(str(ruta_grafico), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  {VERDE}[OK] Gráfico guardado en: {ruta_grafico}{RESET}")


def main() -> None:
    """Función principal del benchmark."""
    print("\n" + "=" * 60)
    print(f"  {NEGRITA}AmazoníaSearch — Benchmark HNSW{RESET}")
    print("=" * 60)

    inicio_total = time.time()

    # Cargar datos
    embeddings, df = cargar_datos()

    # Ejecutar benchmark
    resultados = ejecutar_benchmark(embeddings)

    # Imprimir tabla de resultados
    imprimir_tabla(resultados)

    # Generar gráfico
    generar_grafico_benchmark(resultados)

    # Encontrar la mejor configuración
    mejor = max(resultados, key=lambda r: r["recall_at_10"])
    mas_rapido = min(resultados, key=lambda r: r["tiempo_busqueda_ms"])

    print(f"\n{NEGRITA}Mejor recall:{RESET}")
    print(
        f"  M={mejor['M']}, ef_search={mejor['ef_search']} -> "
        f"Recall@10={mejor['recall_at_10']:.4f}, "
        f"Tiempo={mejor['tiempo_busqueda_ms']:.4f} ms"
    )

    print(f"\n{NEGRITA}Búsqueda más rápida:{RESET}")
    print(
        f"  M={mas_rapido['M']}, ef_search={mas_rapido['ef_search']} -> "
        f"Recall@10={mas_rapido['recall_at_10']:.4f}, "
        f"Tiempo={mas_rapido['tiempo_busqueda_ms']:.4f} ms"
    )

    tiempo_total = time.time() - inicio_total
    print(f"\n  Tiempo total del benchmark: {tiempo_total:.2f} segundos\n")


if __name__ == "__main__":
    main()
