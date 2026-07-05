"""
Motor de Embeddings para AmazoníaSearch.

Este módulo encapsula la lógica de codificación de texto a vectores
utilizando SentenceTransformers con un modelo multilingüe.
"""

import time
import logging
import numpy as np
from sentence_transformers import SentenceTransformer

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Motor de embeddings que utiliza SentenceTransformer para convertir
    texto en vectores densos de dimensión fija (384 dimensiones).
    """

    def __init__(self, model_name: str) -> None:
        """
        Inicializa el motor de embeddings cargando el modelo especificado.

        Args:
            model_name: Nombre del modelo de SentenceTransformer a cargar.
        """
        logger.info(f"Cargando modelo de embeddings: {model_name}")
        inicio = time.time()

        # Cargar el modelo de SentenceTransformer
        self.model: SentenceTransformer = SentenceTransformer(model_name)
        self.model_name: str = model_name

        duracion = time.time() - inicio
        logger.info(
            f"Modelo '{model_name}' cargado exitosamente en {duracion:.2f} segundos"
        )

    def encode(self, text: str) -> np.ndarray:
        """
        Codifica un texto individual en un vector de embeddings.

        Args:
            text: Texto a codificar.

        Returns:
            Vector numpy de dimensión 384 representando el texto.
        """
        logger.debug(f"Codificando texto: '{text[:80]}...'")
        inicio = time.time()

        # Codificar el texto y obtener el vector
        vector: np.ndarray = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        duracion_ms = (time.time() - inicio) * 1000
        logger.debug(
            f"Texto codificado en {duracion_ms:.2f} ms — dimensión: {vector.shape}"
        )

        return vector

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """
        Codifica un lote de textos en una matriz de embeddings.

        Args:
            texts: Lista de textos a codificar.

        Returns:
            Matriz numpy de forma (N, 384) donde N es la cantidad de textos.
        """
        logger.info(f"Codificando lote de {len(texts)} textos...")
        inicio = time.time()

        # Codificar el lote completo de textos
        embeddings: np.ndarray = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )

        duracion = time.time() - inicio
        logger.info(
            f"Lote de {len(texts)} textos codificado en {duracion:.2f} segundos — "
            f"forma: {embeddings.shape}"
        )

        return embeddings
