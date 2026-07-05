"""
Script de verificación de archivos de datos para AmazoníaSearch.

Verifica la existencia y validez de todos los archivos de datos
necesarios para ejecutar la API.

Ejecutar desde la raíz del proyecto:
    python -m backend.scripts.check_files
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ──────────────────────────────────────────────────────────────────────
# Códigos de color ANSI para la salida en consola
# ──────────────────────────────────────────────────────────────────────
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
NEGRITA = "\033[1m"
RESET = "\033[0m"

# ──────────────────────────────────────────────────────────────────────
# Directorio de datos del backend
# ──────────────────────────────────────────────────────────────────────
DIR_DATOS: Path = Path(__file__).resolve().parent.parent / "data"

# Contadores globales de resultados
total_pruebas: int = 0
pruebas_exitosas: int = 0
pruebas_fallidas: int = 0


def exito(mensaje: str) -> None:
    """Imprime un mensaje de éxito en verde."""
    global total_pruebas, pruebas_exitosas
    total_pruebas += 1
    pruebas_exitosas += 1
    print(f"  {VERDE}[OK] PASA{RESET}  {mensaje}")


def fallo(mensaje: str) -> None:
    """Imprime un mensaje de fallo en rojo."""
    global total_pruebas, pruebas_fallidas
    total_pruebas += 1
    pruebas_fallidas += 1
    print(f"  {ROJO}[FAIL] FALLA{RESET} {mensaje}")


def info(mensaje: str) -> None:
    """Imprime un mensaje informativo en azul."""
    print(f"  {AZUL}[INFO] INFO{RESET}  {mensaje}")


def verificar_existencia(nombre: str, ruta: Path) -> bool:
    """
    Verifica si un archivo existe en la ruta especificada.

    Args:
        nombre: Nombre descriptivo del archivo.
        ruta: Ruta completa al archivo.

    Returns:
        True si el archivo existe, False en caso contrario.
    """
    if ruta.exists():
        tamaño = ruta.stat().st_size
        if tamaño >= 1024 * 1024:
            tamaño_str = f"{tamaño / (1024 * 1024):.2f} MB"
        elif tamaño >= 1024:
            tamaño_str = f"{tamaño / 1024:.2f} KB"
        else:
            tamaño_str = f"{tamaño} bytes"
        exito(f"{nombre} existe ({tamaño_str})")
        return True
    else:
        fallo(f"{nombre} NO encontrado en: {ruta}")
        return False


def verificar_dataframe() -> None:
    """Verifica que el DataFrame sea válido y tenga la estructura esperada."""
    ruta = DIR_DATOS / "data.pkl"

    print(f"\n{NEGRITA}[DATAFRAME] Verificando DataFrame (data.pkl){RESET}")
    print("-" * 50)

    if not verificar_existencia("data.pkl", ruta):
        return

    try:
        df = pd.read_pickle(str(ruta))

        # Verificar que es un DataFrame
        if isinstance(df, pd.DataFrame):
            exito(f"Tipo correcto: pandas.DataFrame")
        else:
            fallo(f"Tipo incorrecto: {type(df)}, se esperaba DataFrame")
            return

        # Verificar forma
        filas, columnas = df.shape
        if filas > 0:
            exito(f"Forma: {filas} filas × {columnas} columnas")
        else:
            fallo(f"DataFrame vacío: {filas} filas")

        # Verificar columnas esperadas
        columnas_esperadas = [
            "id", "nombre", "categoria", "descripcion",
            "ubicacion", "latitud", "longitud",
        ]
        columnas_presentes = list(df.columns)
        for col in columnas_esperadas:
            if col in columnas_presentes:
                exito(f"Columna '{col}' presente")
            else:
                fallo(f"Columna '{col}' FALTANTE")

        # Mostrar ejemplo de datos
        info(f"Primera atracción: {df.iloc[0]['nombre']}")
        info(f"Categorías únicas: {df['categoria'].nunique()}")

    except Exception as e:
        fallo(f"Error al cargar data.pkl: {e}")


def verificar_embeddings() -> None:
    """Verifica que los embeddings sean válidos y tengan la forma correcta."""
    ruta = DIR_DATOS / "embeddings.npy"

    print(f"\n{NEGRITA}[EMBEDDINGS] Verificando Embeddings (embeddings.npy){RESET}")
    print("-" * 50)

    if not verificar_existencia("embeddings.npy", ruta):
        return

    try:
        embeddings = np.load(str(ruta))

        # Verificar que es un ndarray
        if isinstance(embeddings, np.ndarray):
            exito(f"Tipo correcto: numpy.ndarray")
        else:
            fallo(f"Tipo incorrecto: {type(embeddings)}")
            return

        # Verificar dimensiones
        if embeddings.ndim == 2:
            exito(f"Dimensiones: 2D (correcto)")
        else:
            fallo(f"Dimensiones: {embeddings.ndim}D (se esperaban 2D)")

        # Verificar forma (N, 384)
        n, dim = embeddings.shape
        exito(f"Forma: {n} vectores × {dim} dimensiones")

        if dim == 384:
            exito(f"Dimensión de embedding: 384 (correcta para MiniLM)")
        else:
            fallo(f"Dimensión de embedding: {dim} (se esperaba 384)")

        # Verificar que no hay valores NaN
        if not np.isnan(embeddings).any():
            exito(f"Sin valores NaN")
        else:
            fallo(f"Se encontraron valores NaN en los embeddings")

        # Verificar normalización
        normas = np.linalg.norm(embeddings, axis=1)
        norma_media = np.mean(normas)
        if abs(norma_media - 1.0) < 0.01:
            exito(f"Vectores normalizados (norma media: {norma_media:.4f})")
        else:
            info(f"Norma media: {norma_media:.4f} (se esperaba ~1.0)")

    except Exception as e:
        fallo(f"Error al cargar embeddings.npy: {e}")


def verificar_indice_hnsw() -> None:
    """Verifica que el índice HNSW sea válido y se pueda cargar."""
    ruta = DIR_DATOS / "hnsw_index.bin"

    print(f"\n{NEGRITA}[INDICE HNSW] Verificando Índice HNSW (hnsw_index.bin){RESET}")
    print("-" * 50)

    if not verificar_existencia("hnsw_index.bin", ruta):
        return

    try:
        import hnswlib

        # Intentar cargar el índice
        indice = hnswlib.Index(space="cosine", dim=384)

        # Primero necesitamos saber cuántos elementos tiene
        # Usamos el DataFrame para obtener el número
        ruta_df = DIR_DATOS / "data.pkl"
        if ruta_df.exists():
            df = pd.read_pickle(str(ruta_df))
            max_elements = len(df)
        else:
            max_elements = 200  # Valor por defecto

        indice.load_index(str(ruta), max_elements=max_elements)

        num_elementos = indice.get_current_count()
        exito(f"Índice cargado correctamente")
        exito(f"Número de elementos: {num_elementos}")

        # Verificar que coincide con los embeddings
        ruta_emb = DIR_DATOS / "embeddings.npy"
        if ruta_emb.exists():
            embeddings = np.load(str(ruta_emb))
            if num_elementos == embeddings.shape[0]:
                exito(
                    f"Cantidad de elementos coincide con embeddings "
                    f"({num_elementos})"
                )
            else:
                fallo(
                    f"Discrepancia: índice tiene {num_elementos} elementos, "
                    f"embeddings tiene {embeddings.shape[0]}"
                )

        # Realizar una búsqueda de prueba
        vector_prueba = np.random.randn(384).astype(np.float32)
        vector_prueba = vector_prueba / np.linalg.norm(vector_prueba)
        indice.set_ef(50)
        ids, distancias = indice.knn_query(vector_prueba.reshape(1, -1), k=3)
        exito(f"Búsqueda de prueba exitosa (top-3 IDs: {ids[0].tolist()})")

    except Exception as e:
        fallo(f"Error al cargar hnsw_index.bin: {e}")


def verificar_csv() -> None:
    """Verifica que el CSV de atracciones exista y sea válido."""
    ruta = DIR_DATOS / "atracciones.csv"

    print(f"\n{NEGRITA}[CSV] Verificando CSV (atracciones.csv){RESET}")
    print("-" * 50)

    if not verificar_existencia("atracciones.csv", ruta):
        return

    try:
        df = pd.read_csv(str(ruta))
        exito(f"CSV leído correctamente: {len(df)} filas × {len(df.columns)} columnas")
        exito(f"Columnas: {list(df.columns)}")
    except Exception as e:
        fallo(f"Error al leer CSV: {e}")


def main() -> None:
    """Función principal que ejecuta todas las verificaciones."""
    print("\n" + "=" * 60)
    print(f"  {NEGRITA}AmazoníaSearch — Verificación de Archivos{RESET}")
    print("=" * 60)
    print(f"  Directorio de datos: {DIR_DATOS}")

    # Ejecutar todas las verificaciones
    verificar_csv()
    verificar_dataframe()
    verificar_embeddings()
    verificar_indice_hnsw()

    # Resumen final
    print("\n" + "=" * 60)
    print(f"  {NEGRITA}RESUMEN{RESET}")
    print("=" * 60)
    print(f"  Total de pruebas:  {total_pruebas}")
    print(f"  {VERDE}Exitosas:        {pruebas_exitosas}{RESET}")
    print(f"  {ROJO}Fallidas:        {pruebas_fallidas}{RESET}")

    if pruebas_fallidas == 0:
        print(
            f"\n  {VERDE}{NEGRITA}¡Todos los archivos son válidos! [OK]{RESET}"
        )
    else:
        print(
            f"\n  {ROJO}{NEGRITA}Se encontraron {pruebas_fallidas} errores. "
            f"Ejecute: python -m backend.scripts.generate_data{RESET}"
        )

    print("=" * 60 + "\n")

    # Código de salida
    sys.exit(0 if pruebas_fallidas == 0 else 1)


if __name__ == "__main__":
    main()
