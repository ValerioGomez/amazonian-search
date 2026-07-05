# 🎬 Guía de Demostración — AmazoníaSearch

> **Guía paso a paso para la presentación en vivo del proyecto ante el docente.**  
> Tiempo estimado de demostración: **15–20 minutos**

---

## 📋 Lista de Verificación Pre-Demo

Antes de la presentación, asegúrate de completar los siguientes pasos:

### Verificación del Entorno

- [ ] **Python 3.10+** instalado y funcionando (`python --version`)
- [ ] **Node.js 18+** instalado y funcionando (`node --version`)
- [ ] Entorno virtual de Python creado y activado (`.\venv\Scripts\Activate.ps1`)
- [ ] Dependencias del backend instaladas (`pip install -r backend/requirements.txt`)
- [ ] Dependencias del frontend instaladas (`cd frontend && npm install`)

### Verificación de Archivos de Datos

- [ ] `backend/data/atracciones.csv` — Dataset original con 110 registros
- [ ] `backend/data/data.pkl` — DataFrame serializado
- [ ] `backend/data/embeddings.npy` — Vectores de embeddings (110 × 384)
- [ ] `backend/data/hnsw_index.bin` — Índice HNSW construido

> 💡 **Si faltan archivos**, ejecuta: `python -m backend.scripts.generate_data`

### Verificación Rápida de Archivos

```bash
python -m backend.scripts.check_files
```

### Preparar las Terminales

Abre **dos terminales** en la raíz del proyecto:

**Terminal 1 — Backend:**

```bash
.\venv\Scripts\Activate.ps1
uvicorn backend.api.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

### Verificación Final

- [ ] Backend respondiendo en: http://localhost:8000
- [ ] Documentación de API visible en: http://localhost:8000/docs
- [ ] Frontend visible en: http://localhost:5173
- [ ] Navegador abierto con ambas pestañas listas

---

## 🎭 Guion de la Demostración

### Paso 1: Presentar la Arquitectura del Sistema (2 min)

**🎤 Qué decir:**

> *"AmazoníaSearch es un buscador semántico inteligente de atractivos turísticos de Puerto Maldonado. El sistema se compone de tres capas principales..."*

**Mostrar** el diagrama de arquitectura del README o dibujar en la pizarra:

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (React + Tailwind + Vite)                     │
│  ┌──────────────────────────────────────────────┐       │
│  │  Barra de búsqueda → Tarjetas de resultados  │       │
│  └──────────────────────────────────────────────┘       │
│                        │ HTTP GET                       │
│                        ▼                                │
│  BACKEND (FastAPI + Python)                             │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────┐     │
│  │  Embedding   │→│   HNSW   │→│  DataLoader    │     │
│  │  Engine      │  │  Engine  │  │  (Pandas)     │     │
│  └──────────────┘  └──────────┘  └───────────────┘     │
│                                                         │
│  DATOS                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  │ data.pkl │  │ .npy     │  │ hnsw_index.bin   │      │
│  └──────────┘  └──────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**Puntos clave a mencionar:**

1. El **Embedding Engine** usa el modelo `paraphrase-multilingual-MiniLM-L12-v2` para transformar texto en vectores de 384 dimensiones.
2. El **HNSW Engine** usa `hnswlib` para buscar los vecinos más cercanos en el espacio vectorial.
3. No usamos base de datos relacional — los datos están en memoria como un DataFrame de Pandas (`data.pkl`).

---

### Paso 2: Mostrar el Dataset (2 min)

**🎤 Qué decir:**

> *"Nuestro dataset contiene 110 atractivos turísticos reales de Puerto Maldonado, organizados en 7 campos..."*

**Abrir** el archivo `data/atracciones.csv` y mostrar las columnas:

| Campo | Descripción | Ejemplo |
|:---|:---|:---|
| `id` | Identificador único | 1 |
| `nombre` | Nombre del atractivo | Lago Sandoval |
| `categoria` | Tipo de atractivo | Reserva Natural |
| `descripcion` | Descripción detallada en español | *Hermoso lago de herradura...* |
| `ubicacion` | Ubicación geográfica | Reserva Nacional Tambopata |
| `latitud` | Coordenada latitud | -12.6125 |
| `longitud` | Coordenada longitud | -69.1778 |

**Destacar:**

- Las categorías incluyen: Reserva Natural, Alojamiento, Aventura, Atracción Cultural, Santuario de Vida Silvestre, Mirador, entre otras.
- Las descripciones están en **español** y son lo suficientemente detalladas para generar embeddings significativos.
- El modelo multilingüe entiende español nativamente.

---

### Paso 3: Iniciar el Backend (2 min)

**🎤 Qué decir:**

> *"Ahora vamos a iniciar el servidor. Observen los logs de carga..."*

**Ejecutar** en la Terminal 1 (si no está ya corriendo):

```bash
uvicorn backend.api.main:app --reload --port 8000
```

**Señalar en los logs:**

1. ✅ **Carga del modelo:** *"Cargando modelo de embeddings..."* — El modelo SentenceTransformers se carga en memoria.
2. ✅ **Carga de datos:** *"Cargando datos..."* — El DataFrame se deserializa desde `data.pkl`.
3. ✅ **Carga del índice:** *"Cargando índice HNSW..."* — El índice se carga desde `hnsw_index.bin`.
4. ✅ **Servidor listo:** *"Uvicorn running on http://127.0.0.1:8000"*

**Mostrar** la documentación automática de la API en: http://localhost:8000/docs

> 💡 *"FastAPI genera automáticamente esta documentación interactiva tipo Swagger. Podemos probar cada endpoint directamente desde el navegador."*

---

### Paso 4: Abrir el Frontend (1 min)

**🎤 Qué decir:**

> *"Esta es la interfaz de usuario construida con React y Tailwind CSS..."*

**Abrir** http://localhost:5173 en el navegador.

**Señalar:**

- La barra de búsqueda central
- El diseño responsivo con temática amazónica
- Los iconos de Lucide React

---

### Paso 5: Realizar Búsquedas en Vivo (5 min)

Este es el **momento más importante** de la demostración. Realiza las siguientes búsquedas en orden:

#### 🔍 Búsqueda 1: *"lugar tranquilo para ver aves en la selva"*

**🎤 Qué decir antes de buscar:**

> *"Observen que vamos a buscar en lenguaje natural, no con palabras clave. El sistema debe entender el CONCEPTO de lo que buscamos."*

**Resultados esperados:**
- 🏆 **Lago Sandoval** — Reserva Natural (lugar con aves exóticas como guacamayos y tucanes)
- **Collpa de Guacamayos Chuncho** — Donde se reúnen cientos de guacamayos
- **Reserva Ecológica Taricaya** — Centro de rescate con observación de fauna

**🎤 Qué decir después:**

> *"El sistema encontró el Lago Sandoval como primer resultado, a pesar de que en su descripción no aparece literalmente 'lugar tranquilo'. Esto es porque el modelo de IA entendió la SEMÁNTICA de nuestra consulta: un lago rodeado de vegetación donde hay aves exóticas ES conceptualmente un lugar tranquilo para ver aves."*

#### 🔍 Búsqueda 2: *"alojamiento ecológico con vista al lago"*

**Resultados esperados:**
- 🏆 **Inkaterra Hacienda Concepción** — Eco-lodge de lujo con cabañas
- **Corto Maltes Amazonia Lodge** — Eco-lodge cerca del Lago Sandoval
- **Posada Amazonas Lodge** — Eco-lodge galardonado

**🎤 Qué decir después:**

> *"Busqué 'alojamiento ecológico' y el sistema devuelve eco-lodges. El término 'eco-lodge' y 'alojamiento ecológico' son semánticamente equivalentes para el modelo, aunque las palabras sean diferentes."*

#### 🔍 Búsqueda 3: *"aventura en la selva amazónica"*

**Resultados esperados:**
- 🏆 **Pasarela de Dosel de Taricaya** — Aventura aérea sobre el dosel
- **Quebrada Gamitana** — Kayak y caimanes al atardecer
- **Lago Valencia** — Excursión con pesca de pirañas

**🎤 Qué decir después:**

> *"Para 'aventura', el sistema sugiere actividades de aventura como kayak, dosel y pesca de pirañas. Esto demuestra que comprende el campo semántico de la palabra 'aventura' y lo relaciona con actividades emocionantes."*

---

### Paso 6: Explicar Cómo Funciona HNSW (3 min)

**🎤 Qué decir:**

> *"Ahora expliquemos QUÉ pasó detrás de escena cuando realizamos esa búsqueda..."*

**Dibujar en la pizarra o mostrar el siguiente diagrama:**

```
                    CONSULTA: "aventura en la selva"
                              │
                              ▼
                    ┌──────────────────┐
                    │ Modelo de IA     │
                    │ (SentenceTransf.)│
                    └──────────────────┘
                              │
                    Vector de 384 dimensiones
                    [0.12, -0.45, 0.78, ...]
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │              ÍNDICE HNSW                │
        │                                         │
        │  Capa 2:  A ──────────── D              │
        │           │     busca    │              │
        │           ▼ codiciosa    ▼              │
        │  Capa 1:  A ── B ── C ── D ── E        │
        │                │                        │
        │                ▼  baja                  │
        │  Capa 0:  A-B-C-D-E-F-G-H-I-J-K        │
        │               ▲▲▲                       │
        │           k=3 vecinos                   │
        └─────────────────────────────────────────┘
                              │
                    IDs: [15, 23, 7]
                    Distancias: [0.13, 0.18, 0.22]
                              │
                              ▼
                    Resultado: Pasarela de Dosel,
                               Quebrada Gamitana,
                               Lago Valencia
```

**Explicar punto por punto:**

1. **Transformación a vector:** La consulta se convierte en un vector de 384 números usando el modelo `paraphrase-multilingual-MiniLM-L12-v2`.

2. **Navegación codiciosa (Greedy Search):** El algoritmo comienza en la **capa más alta** del grafo (con pocos nodos) y se mueve hacia el vecino más cercano al vector de consulta.

3. **Descenso por capas:** Cuando no puede mejorar en una capa, **desciende** a la capa inferior (con más nodos y conexiones más finas).

4. **Resultado en la capa 0:** En la capa base, realiza una búsqueda más detallada y retorna los K vecinos más cercanos.

5. **Complejidad O(log N):** Gracias a la estructura jerárquica (similar a un Skip List), la búsqueda tiene complejidad logarítmica en lugar de lineal.

**🎤 Analogía clave:**

> *"Es como buscar una dirección: primero tomas la autopista (capa superior) para llegar a la ciudad correcta, luego tomas calles principales (capa intermedia), y finalmente calles locales (capa base) para llegar a la casa exacta. No necesitas recorrer TODAS las calles de TODAS las ciudades."*

---

### Paso 7: Mostrar los Resultados Experimentales (2 min)

**🎤 Qué decir:**

> *"Realizamos experimentos variando los parámetros del índice HNSW para evaluar el trade-off entre velocidad y precisión..."*

**Mostrar** los gráficos generados en `backend/data/`:

1. **Gráfico de Variación de M:** Muestra cómo al aumentar M, mejora el recall pero aumenta el tiempo de construcción y el uso de memoria.

2. **Gráfico de Recall vs. Velocidad:** Muestra la relación entre `ef_search` y la precisión de los resultados.

**Destacar:**

> *"Elegimos M=16 y ef_search=50 porque ofrecen el mejor balance entre velocidad y precisión para nuestro dataset de 110 elementos. Con solo 110 elementos, la diferencia de velocidad es mínima, pero en datasets de millones de elementos, estos parámetros se vuelven críticos."*

---

### Paso 8: Benchmark (1 min)

**Ejecutar** el benchmark si el tiempo lo permite:

```bash
python -m backend.scripts.benchmark
```

**Señalar:**
- Tiempo promedio de búsqueda en microsegundos
- Comparativa con búsqueda por fuerza bruta
- Recall@K del índice HNSW

---

## 🎯 Puntos Clave para el Docente

Durante la presentación, asegúrate de mencionar estos puntos que demuestran dominio del tema:

### 1. Sobre la Estructura de Datos (HNSW)

- HNSW es un **grafo jerárquico** con múltiples capas, similar a un Skip List.
- El parámetro **M** controla la conectividad del grafo (más M = más conexiones = mayor recall pero más memoria).
- El parámetro **ef_construction** controla la calidad del índice durante la construcción.
- El parámetro **ef_search** controla el trade-off velocidad/precisión durante la búsqueda.
- La complejidad de búsqueda es **O(log N)**, versus O(N) de fuerza bruta.

### 2. Sobre los Embeddings

- Un embedding es la **representación numérica del significado** de un texto.
- Textos con significados similares tienen vectores **cercanos** en el espacio de 384 dimensiones.
- Usamos **Similitud de Coseno** porque mide el ángulo entre vectores, no la magnitud.
- El modelo `paraphrase-multilingual-MiniLM-L12-v2` fue entrenado en 50+ idiomas.

### 3. Sobre la Arquitectura

- Arquitectura **desacoplada**: Frontend y Backend son independientes y se comunican vía API REST.
- Sin base de datos relacional: usamos `data.pkl` cargado en **memoria** para máxima velocidad.
- El índice HNSW se **serializa** a disco (`hnsw_index.bin`) y se carga al iniciar el servidor.

### 4. Sobre la Diferencia con Búsqueda Tradicional

- Búsqueda tradicional (SQL LIKE): *"aves"* solo encuentra registros que contengan la palabra *"aves"*.
- Búsqueda semántica (HNSW + embeddings): *"lugar para ver pájaros"* encuentra registros sobre aves, tucanes, guacamayos, etc.

---

## ❓ Posibles Preguntas y Respuestas

### P1: *"¿Por qué HNSW y no KD-Trees?"*

> **R:** Los KD-Trees sufren la **maldición de la dimensionalidad** — su rendimiento se degrada exponencialmente cuando la dimensionalidad supera las 10-20 dimensiones. Nuestros vectores tienen **384 dimensiones**, donde los KD-Trees no son mejores que la fuerza bruta. HNSW mantiene complejidad **O(log N)** independientemente de la dimensionalidad.

### P2: *"¿Por qué Similitud de Coseno y no Distancia Euclidiana?"*

> **R:** La Similitud de Coseno mide el **ángulo** entre vectores, no su magnitud. Esto es ideal para embeddings de texto porque dos oraciones con el mismo significado pero diferente longitud tendrán vectores que apuntan en la **misma dirección** (ángulo pequeño) aunque su magnitud sea diferente.

### P3: *"¿Qué pasa si el usuario busca en inglés?"*

> **R:** El modelo `paraphrase-multilingual-MiniLM-L12-v2` fue entrenado en **50+ idiomas**. Si el usuario busca *"peaceful lake for birdwatching"*, el sistema debería encontrar resultados similares a *"lugar tranquilo para ver aves"*, ya que el modelo entiende la equivalencia semántica entre idiomas.

### P4: *"¿El resultado es exacto o aproximado?"*

> **R:** Es **aproximado (ANN — Approximate Nearest Neighbor)**. HNSW sacrifica una fracción mínima de precisión a cambio de una mejora dramática en velocidad. En la práctica, con `ef_search=50`, el recall supera el 95% en nuestro dataset.

### P5: *"¿Cómo escala esto a millones de registros?"*

> **R:** HNSW es una de las estructuras **más escalables** para búsqueda vectorial. Sistemas como Pinecone, Milvus y Weaviate usan HNSW internamente. La complejidad O(log N) significa que duplicar el dataset solo agrega una operación adicional a la búsqueda.

### P6: *"¿Qué modelo de IA usan y por qué ese?"*

> **R:** Usamos `paraphrase-multilingual-MiniLM-L12-v2` de la familia SentenceTransformers (SBERT). Lo elegimos porque: (1) es **multilingüe** y entiende español, (2) genera vectores de **384 dimensiones** (compactos pero expresivos), (3) es **rápido** (modelo "mini"), y (4) está optimizado para medir **similitud semántica** entre oraciones.

### P7: *"¿Por qué no usan una base de datos como PostgreSQL?"*

> **R:** Para un dataset de 110 elementos, cargar los datos directamente en memoria como un DataFrame de Pandas es más eficiente y simple. PostgreSQL agregaría complejidad innecesaria. Sin embargo, en un sistema de producción con miles de registros y múltiples usuarios concurrentes, sí sería recomendable usar una base de datos.

### P8: *"¿Cuál es la diferencia entre ef_construction y ef_search?"*

> **R:** `ef_construction` se usa **al construir** el índice: controla cuántos candidatos se evalúan al insertar cada nodo (más alto = índice de mejor calidad pero construcción más lenta). `ef_search` se usa **al buscar**: controla cuántos candidatos se evalúan durante la búsqueda (más alto = resultados más precisos pero búsqueda más lenta).

---

## 🔧 Guía de Solución de Problemas

### El backend no inicia

| Problema | Causa Probable | Solución |
|:---|:---|:---|
| `ModuleNotFoundError` | Dependencias no instaladas | `pip install -r backend/requirements.txt` |
| `FileNotFoundError: data.pkl` | Datos no generados | `python -m backend.scripts.generate_data` |
| `Port 8000 already in use` | Puerto ocupado | Cambiar puerto: `--port 8001` o matar el proceso |
| `CUDA error` | Problema con GPU | El modelo funciona en CPU por defecto |

### El frontend no inicia

| Problema | Causa Probable | Solución |
|:---|:---|:---|
| `npm ERR! missing` | `node_modules` no instalados | `cd frontend && npm install` |
| `ENOSPC` | Límite de watchers | Aumentar `fs.inotify.max_user_watches` |
| Página en blanco | Backend no conectado | Verificar que el backend esté en http://localhost:8000 |

### Los resultados de búsqueda son malos

| Problema | Causa Probable | Solución |
|:---|:---|:---|
| Resultados irrelevantes | `ef_search` muy bajo | Aumentar `ef_search` en `hnsw_engine.py` |
| Pocos resultados | `k` muy bajo | Aumentar `k` en la consulta (`?k=10`) |
| Resultados lentos | Modelo cargándose | Esperar a que la primera consulta inicialice el modelo |

### Regenerar todos los datos desde cero

```bash
# Eliminar datos existentes
del backend\data\data.pkl
del backend\data\embeddings.npy
del backend\data\hnsw_index.bin

# Regenerar
python -m backend.scripts.generate_data
```

---

## ⏱️ Cronograma Sugerido de la Presentación

| Tiempo | Actividad | Duración |
|:---:|:---|:---:|
| 0:00 | Presentación e introducción | 1 min |
| 1:00 | Arquitectura del sistema | 2 min |
| 3:00 | Dataset y modelo de datos | 2 min |
| 5:00 | Inicio del backend (logs) | 2 min |
| 7:00 | Interfaz de usuario | 1 min |
| 8:00 | **Búsquedas en vivo (momento clave)** | **5 min** |
| 13:00 | Explicación técnica de HNSW | 3 min |
| 16:00 | Resultados experimentales | 2 min |
| 18:00 | Preguntas y respuestas | 2 min |
| **20:00** | **Fin** | |

---

> 🎯 **Consejo final:** Practica la demo completa al menos una vez antes de la presentación. Asegúrate de que todas las búsquedas devuelvan resultados coherentes y ten preparadas las respuestas a las preguntas frecuentes.
