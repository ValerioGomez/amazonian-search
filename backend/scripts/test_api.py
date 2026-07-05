"""
Script de prueba de la API de AmazoníaSearch.

Realiza pruebas a todos los endpoints de la API en ejecución:
- GET /          → Información del sistema
- GET /health    → Estado de salud
- GET /attractions → Lista de atracciones
- GET /categories  → Lista de categorías
- POST /search   → Búsqueda semántica con múltiples consultas

Ejecutar desde la raíz del proyecto (con la API corriendo):
    python -m backend.scripts.test_api
"""

import sys
import json

import requests

# ──────────────────────────────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────────────────────────────
URL_BASE = "http://localhost:8000"

# Colores ANSI para la salida
VERDE = "\033[92m"
ROJO = "\033[91m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
CIAN = "\033[96m"
NEGRITA = "\033[1m"
RESET = "\033[0m"

# Consultas de prueba para búsqueda semántica
CONSULTAS_PRUEBA: list[str] = [
    "lugar tranquilo para ver aves en la selva",
    "alojamiento ecológico con vista al lago",
    "reserva natural para caminatas",
    "donde puedo ver guacamayos al amanecer",
    "hotel cerca del río Madre de Dios",
    "lago para nadar y relajarse",
    "aventura en la selva amazónica",
]


def separador(titulo: str) -> None:
    """Imprime un separador con título para organizar la salida."""
    print(f"\n{'=' * 60}")
    print(f"  {NEGRITA}{titulo}{RESET}")
    print(f"{'=' * 60}")


def probar_raiz() -> bool:
    """
    Prueba el endpoint GET / (información del sistema).

    Returns:
        True si la prueba fue exitosa.
    """
    separador("GET / — Información del Sistema")
    try:
        respuesta = requests.get(f"{URL_BASE}/", timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        print(f"  {VERDE}[OK] Estado: {respuesta.status_code}{RESET}")
        print(f"  Proyecto: {datos.get('proyecto', 'N/A')}")
        print(f"  Versión: {datos.get('version', 'N/A')}")
        print(f"  Modelo: {datos.get('modelo', 'N/A')}")
        print(f"  Atracciones: {datos.get('num_atracciones', 'N/A')}")

        parametros = datos.get("parametros_hnsw", {})
        if parametros:
            print(f"  Parámetros HNSW:")
            for clave, valor in parametros.items():
                print(f"    - {clave}: {valor}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"  {ROJO}[ERR] Error de conexión. ¿Está la API ejecutándose?{RESET}")
        print(f"  {AMARILLO}  Inicie con: uvicorn backend.api.main:app --reload --port 8000{RESET}")
        return False
    except Exception as e:
        print(f"  {ROJO}[ERR] Error: {e}{RESET}")
        return False


def probar_salud() -> bool:
    """
    Prueba el endpoint GET /health (estado de salud).

    Returns:
        True si la prueba fue exitosa.
    """
    separador("GET /health — Estado de Salud")
    try:
        respuesta = requests.get(f"{URL_BASE}/health", timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        print(f"  {VERDE}[OK] Estado: {respuesta.status_code}{RESET}")
        print(f"  status: {datos.get('status', 'N/A')}")
        print(f"  Modelo cargado: {datos.get('modelo_cargado', 'N/A')}")
        print(f"  Índice cargado: {datos.get('indice_cargado', 'N/A')}")
        print(f"  Datos cargados: {datos.get('datos_cargados', 'N/A')}")

        # Verificar que todos los componentes estén cargados
        if all([
            datos.get("modelo_cargado"),
            datos.get("indice_cargado"),
            datos.get("datos_cargados"),
        ]):
            print(f"  {VERDE}[OK] Todos los componentes cargados correctamente{RESET}")
        else:
            print(f"  {AMARILLO}[WARN] Algunos componentes no están cargados{RESET}")

        return True

    except Exception as e:
        print(f"  {ROJO}[ERR] Error: {e}{RESET}")
        return False


def probar_atracciones() -> bool:
    """
    Prueba el endpoint GET /attractions (lista de atracciones).

    Returns:
        True si la prueba fue exitosa.
    """
    separador("GET /attractions — Lista de Atracciones")
    try:
        # Prueba sin filtro
        respuesta = requests.get(
            f"{URL_BASE}/attractions",
            params={"limit": 5, "offset": 0},
            timeout=10,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        total = datos.get("total", 0)
        atracciones = datos.get("atracciones", [])

        print(f"  {VERDE}[OK] Estado: {respuesta.status_code}{RESET}")
        print(f"  Total de atracciones: {total}")
        print(f"  Mostrando primeras {len(atracciones)}:")

        for attr in atracciones:
            print(
                f"    - [{attr.get('id')}] {attr.get('nombre')} "
                f"({CIAN}{attr.get('categoria')}{RESET})"
            )

        # Prueba con filtro de categoría
        if atracciones:
            primera_cat = atracciones[0].get("categoria", "")
            resp_filtrada = requests.get(
                f"{URL_BASE}/attractions",
                params={"categoria": primera_cat, "limit": 3},
                timeout=10,
            )
            if resp_filtrada.status_code == 200:
                datos_filt = resp_filtrada.json()
                print(
                    f"\n  {VERDE}[OK] Filtro por '{primera_cat}': "
                    f"{datos_filt.get('total', 0)} resultados{RESET}"
                )

        return True

    except Exception as e:
        print(f"  {ROJO}[ERR] Error: {e}{RESET}")
        return False


def probar_categorias() -> bool:
    """
    Prueba el endpoint GET /categories (categorías únicas).

    Returns:
        True si la prueba fue exitosa.
    """
    separador("GET /categories — Categorías")
    try:
        respuesta = requests.get(f"{URL_BASE}/categories", timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        categorias = datos.get("categorias", [])
        total = datos.get("total", 0)

        print(f"  {VERDE}[OK] Estado: {respuesta.status_code}{RESET}")
        print(f"  Total de categorías: {total}")
        for cat in categorias:
            print(f"    - {cat}")

        return True

    except Exception as e:
        print(f"  {ROJO}[ERR] Error: {e}{RESET}")
        return False


def probar_busqueda() -> bool:
    """
    Prueba el endpoint POST /search con múltiples consultas semánticas.

    Returns:
        True si todas las pruebas fueron exitosas.
    """
    separador("POST /search — Búsqueda Semántica")
    exitos = 0

    for i, consulta in enumerate(CONSULTAS_PRUEBA, 1):
        print(f"\n  {NEGRITA}Consulta {i}/{len(CONSULTAS_PRUEBA)}:{RESET}")
        print(f"  {AZUL}> \"{consulta}\"{RESET}")

        try:
            respuesta = requests.post(
                f"{URL_BASE}/search",
                json={"query": consulta, "k": 5},
                timeout=30,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()

            tiempo = datos.get("tiempo_busqueda_ms", 0)
            resultados = datos.get("resultados", [])
            total = datos.get("total_resultados", 0)

            print(
                f"  {VERDE}[OK] {total} resultados en {tiempo:.2f} ms{RESET}"
            )

            # Mostrar los resultados con similitud
            for j, res in enumerate(resultados, 1):
                similitud = res.get("similitud", 0)

                # Color según nivel de similitud
                if similitud >= 70:
                    color_sim = VERDE
                elif similitud >= 50:
                    color_sim = AMARILLO
                else:
                    color_sim = ROJO

                print(
                    f"    {j}. {color_sim}{similitud:5.1f}%{RESET} — "
                    f"{res.get('nombre', 'N/A')} "
                    f"({CIAN}{res.get('categoria', 'N/A')}{RESET})"
                )

            exitos += 1

        except requests.exceptions.ConnectionError:
            print(f"  {ROJO}[ERR] Error de conexión{RESET}")
        except Exception as e:
            print(f"  {ROJO}[ERR] Error: {e}{RESET}")

    return exitos == len(CONSULTAS_PRUEBA)


def main() -> None:
    """Función principal que ejecuta todas las pruebas de la API."""
    print("\n" + "=" * 60)
    print(f"  {NEGRITA}AmazoníaSearch — Pruebas de API{RESET}")
    print(f"  URL base: {URL_BASE}")
    print("=" * 60)

    # Verificar conexión con la prueba de raíz
    if not probar_raiz():
        print(
            f"\n{ROJO}No se pudo conectar a la API. Asegúrese de que esté ejecutándose.{RESET}"
        )
        sys.exit(1)

    # Ejecutar el resto de las pruebas
    resultados: dict[str, bool] = {
        "GET /": True,  # Ya se probó arriba
        "GET /health": probar_salud(),
        "GET /attractions": probar_atracciones(),
        "GET /categories": probar_categorias(),
        "POST /search": probar_busqueda(),
    }

    # Resumen final
    separador("RESUMEN DE PRUEBAS")
    exitosas = sum(1 for v in resultados.values() if v)
    fallidas = sum(1 for v in resultados.values() if not v)

    for endpoint, ok in resultados.items():
        estado = f"{VERDE}[OK] PASA{RESET}" if ok else f"{ROJO}[ERR] FALLA{RESET}"
        print(f"  {estado}  {endpoint}")

    print(f"\n  Total: {len(resultados)} | "
          f"{VERDE}Exitosas: {exitosas}{RESET} | "
          f"{ROJO}Fallidas: {fallidas}{RESET}")

    if fallidas == 0:
        print(f"\n  {VERDE}{NEGRITA}¡Todas las pruebas pasaron! [OK]{RESET}\n")
    else:
        print(f"\n  {ROJO}{NEGRITA}Algunas pruebas fallaron [ERR]{RESET}\n")

    sys.exit(0 if fallidas == 0 else 1)


if __name__ == "__main__":
    main()
