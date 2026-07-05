"""
Motor HNSW para AmazoníaSearch.

Este módulo gestiona el índice HNSW (Hierarchical Navigable Small World)
para la búsqueda aproximada de vecinos más cercanos (ANN).
"""

import logging
import numpy as np
import hnswlib

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


class HNSWEngine:
    """
    Motor de búsqueda basado en el algoritmo HNSW para encontrar
    los vectores más similares de forma eficiente.
    """

    def __init__(self, dim: int, space: str = "cosine") -> None:
        """
        Inicializa el motor HNSW con la dimensión y métrica de distancia.

        Args:
            dim: Dimensión de los vectores (384 para MiniLM).
            space: Métrica de distancia ('cosine', 'l2' o 'ip').
        """
        self.dim: int = dim
        self.space: str = space
        self.index: hnswlib.Index | None = None

        logger.info(
            f"Motor HNSW inicializado — dimensión: {dim}, espacio: {space}"
        )

    def load_index(self, path: str, max_elements: int) -> None:
        """
        Carga un índice HNSW existente desde un archivo .bin.

        Args:
            path: Ruta al archivo del índice HNSW.
            max_elements: Número máximo de elementos del índice.
        """
        logger.info(f"Cargando índice HNSW desde: {path}")

        # Crear una nueva instancia del índice con las dimensiones correctas
        self.index = hnswlib.Index(space=self.space, dim=self.dim)

        # Cargar el índice directamente desde el archivo
        # load_index inicializa la estructura interna del índice automáticamente
        self.index.load_index(str(path), max_elements=max_elements)

        num_elementos = self.index.get_current_count()
        logger.info(
            f"Índice HNSW cargado exitosamente — "
            f"{num_elementos} elementos en el índice"
        )

    def build_index(
        self,
        embeddings: np.ndarray,
        M: int = 16,
        ef_construction: int = 200,
    ) -> None:
        """
        Construye un nuevo índice HNSW a partir de una matriz de embeddings.

        Args:
            embeddings: Matriz numpy de forma (N, dim) con los vectores.
            M: Número de conexiones por nodo en el grafo HNSW.
            ef_construction: Factor de calidad durante la construcción.
        """
        num_elementos = embeddings.shape[0]
        logger.info(
            f"Construyendo índice HNSW — "
            f"{num_elementos} elementos, M={M}, ef_construction={ef_construction}"
        )

        # Crear e inicializar el índice
        self.index = hnswlib.Index(space=self.space, dim=self.dim)
        self.index.init_index(
            max_elements=num_elementos,
            M=M,
            ef_construction=ef_construction,
        )

        # Agregar todos los vectores al índice
        ids = np.arange(num_elementos)
        self.index.add_items(embeddings, ids)

        logger.info(
            f"Índice HNSW construido exitosamente — "
            f"{self.index.get_current_count()} elementos indexados"
        )

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        ef_search: int = 50,
    ) -> tuple[list[int], list[float]]:
        """
        Busca los k vecinos más cercanos a un vector de consulta.

        Las distancias devueltas por hnswlib en espacio coseno son
        (1 - similitud_coseno). Para obtener el porcentaje de similitud:
        similitud = (1 - distancia) * 100

        Args:
            query_vector: Vector de consulta de dimensión 384.
            k: Número de resultados a devolver.
            ef_search: Parámetro de calidad de búsqueda.

        Returns:
            Tupla de (ids, distancias) donde:
                - ids: Lista de identificadores de los vecinos más cercanos.
                - distancias: Lista de distancias (1 - similitud_coseno).
        """
        if self.index is None:
            logger.error("No se puede buscar: el índice HNSW no está cargado")
            raise ValueError("El índice HNSW no ha sido cargado o construido")

        # Configurar el parámetro ef de búsqueda
        self.index.set_ef(ef_search)

        # Asegurar que el vector tenga la forma correcta (1, dim)
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Realizar la búsqueda de vecinos más cercanos
        ids, distances = self.index.knn_query(query_vector, k=k)

        # Convertir los resultados a listas planas
        ids_lista: list[int] = ids[0].tolist()
        distancias_lista: list[float] = distances[0].tolist()

        logger.debug(
            f"Búsqueda HNSW completada — k={k}, ef_search={ef_search}, "
            f"distancia mínima: {min(distancias_lista):.4f}"
        )

        return ids_lista, distancias_lista

    def get_info(self) -> dict:
        """
        Retorna metadatos e información del índice HNSW actual.

        Returns:
            Diccionario con información del índice:
                - espacio: Métrica de distancia utilizada.
                - dimension: Dimensión de los vectores.
                - num_elementos: Cantidad de elementos en el índice.
                - M: Parámetro M del grafo HNSW.
                - ef_construction: Factor de construcción utilizado.
        """
        info: dict = {
            "espacio": self.space,
            "dimension": self.dim,
            "num_elementos": 0,
            "M": None,
            "ef_construction": None,
        }

        if self.index is not None:
            info["num_elementos"] = self.index.get_current_count()
            # Obtener parámetros internos del índice si están disponibles
            try:
                info["M"] = self.index.M
                info["ef_construction"] = self.index.ef_construction
            except AttributeError:
                logger.warning(
                    "No se pudieron obtener los parámetros M y ef_construction del índice"
                )

        return info
