# Página 1

Trabajo Final de Investigación\
Estructura de Datos y Algoritmos Avanzado

Parte 1: Lista Consolidada de Temas de Estructuras Multidimensionales y
Búsqueda Geométrica Esta lista resume el ecosistema completo que los
estudiantes pueden investigar para el presente trabajo: 1. Estructuras
de Partición del Espacio (Árboles): KD-Trees, Quadtrees, Octrees y
BSP-Trees. 2. Estructuras de Partición de Datos (Contenedores): R-Trees,
R\*-Trees y R+-Trees (enfoque GIS). 3. Árboles en Espacios Métricos
Puros: Vantage-Point Trees (VP-Trees) y BK- Trees (búsqueda por
distancias discretas/texto). 4. Técnicas de Proyección Probabilística:
Locality-Sensitive Hashing (LSH). 5. Grafos de Proximidad Avanzados:
KNN-Graphs, Grafos de Vecindario Relativo (RNG), Navigable Small World
(NSW) y Hierarchical Navigable Small World (HNSW).

Parte 2: Propuesta de Trabajo de Investigación y Desarrollo Título
sugerido para el alumno/grupo: Se debe utilizar cualquier estructura de
datos mencionados en el paso 1, por ejemplo si utilizamos HNSW se podría
plantear el titulo\
"Implementación de un Índice de Búsqueda Vectorial Basado en HNSW para
la Recuperación Semántica Avanzada de Información en un Sistema de
Asistencia Turística Local" . 1. Resumen del Proyecto El trabajo
consiste en investigar a fondo la estructura de datos HNSW (Hierarchical
Navigable Small World) basada en el artículo cientíﬁco de Malkov y
Yashunin, para luego desarrollar una aplicación práctica: un Buscador
Semántico Inteligente de Atractivos Turísticos de la Región (por
ejemplo, Puno). A diferencia de un buscador tradicional que busca
palabras exactas, esta aplicación entenderá el contexto y signiﬁcado de
la consulta del usuario (por ejemplo, si el usuario busca "un lugar
tranquilo en el lago para ver el atardecer", el

# Página 2

sistema debe sugerir la Isla Taquile o Amantaní, aunque la descripción
no contenga explícitamente esas palabras). 2. Marco Tecnológico y
Arquitectura de la Aplicación Para que el proyecto sea viable, moderno y
aplicable a la ingeniería de software actual, se propone la siguiente
arquitectura:  Backend: Desarrollado en C#, Python, Java, Python u
otro. Se encargará de gestionar la lógica de negocio, las peticiones API
y la conexión con el motor de vectores.  Frontend: Una interfaz limpia,
rápida y responsiva construida como una Single Page Application (SPA)
usando Vue.js, Angular o React y estilizada con Tailwind CSS, Bootstrap
u otros.  Generación de Embeddings (Vectores): Uso de un modelo de
Inteligencia Artiﬁcial de código abierto (como all-MiniLM-L6-v2 de
Hugging Face mediante una pequeña API en Python o una librería
equivalente) para transformar las descripciones de los lugares
turísticos en vectores numéricos de alta dimensionalidad (por ejemplo,
384 dimensiones).  Motor de Búsqueda (La Estructura de Datos):
Implementación o integración de un índice HNSW (puede ser usando la
librería nativa hnswlib o bases de datos como ChromaDB / Pinecone, o una
aproximación propia en código para evaluar algoritmos) que recibirá el
vector de la consulta del usuario y devolverá en microsegundos los
vecinos más cercanos (los atractivos turísticos más similares). 3. Fases
del Trabajo de Investigación Fase I: Fundamentación Teórica y Estado del
Arte  El alumno deberá redactar una monografía explicando la evolución
matemática: desde la ineﬁciencia de los KD-Trees en alta dimensionalidad
(la maldición de la dimensionalidad), pasando por la aproximación
probabilística de NSW, hasta llegar a la jerarquía logarítmica O(log N)
de HNSW.  Deberá justiﬁcar matemáticamente la elección de la métrica de
distancia (por ejemplo, Similitud de Coseno o Distancia Euclidiana) para
comparar los vectores de texto. Fase II: Modelado e Ingesta de Datos 
Creación de un Dataset con al menos 100 atractivos turísticos detallados
de la región (hoteles, paisajes, restaurantes, rutas históricas).

# Página 3

 Procesamiento del texto: Pasar cada descripción por el modelo de IA
para generar su representación vectorial.  Construcción del índice HNSW
insertando de forma incremental cada vector, conﬁgurando correctamente
los hiperparámetros críticos analizados en el artículo cientíﬁco (M,
Mmax0 ,efConstruction). Fase III: Desarrollo del Sistema Web  API Rest:
Crear los endpoints para recibir las búsquedas del usuario, enviar la
consulta al índice HNSW, recuperar los IDs de los vecinos más cercanos y
consultar los detalles completos en una base de datos relacional
(MySQL/PostgreSQL).  Interfaz de Usuario: Diseñar una barra de búsqueda
inteligente interactiva. Al escribir la consulta, se mostrarán las
tarjetas de los lugares turísticos ordenadas por su "porcentaje de
similitud semántica" en tiempo real. 4. Entregables del Proyecto para la
Evaluación Para garantizar el rigor académico, el grupo o alumno deberá
presentar: 1. Informe de Investigación (Formato IEEE u otro):
Introducción, marco teórico, metodología del algoritmo HNSW (con
diagramas de las capas del grafo construidas), experimentos variando el
parámetro M para medir el trade-oƯ entre velocidad y precisión, y
conclusiones. 2. Código Fuente: Repositorio en GitHub con el código
limpio y ordenado del Backend y Frontend. 3. Demostración en Vivo:
Explicación en el salón de cómo la búsqueda codiciosa navega por las
capas superiores del grafo HNSW para encontrar un atractivo turístico en
microsegundos.
