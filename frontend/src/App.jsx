import { useState, useEffect, useCallback } from 'react'
import { TreePine, Leaf, Github, BookOpen } from 'lucide-react'
import SearchBar from './components/SearchBar'
import ResultsGrid from './components/ResultsGrid'
import Stats from './components/Stats'

// URL base de la API configurada desde variables de entorno
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Sugerencias de búsqueda predefinidas para mostrar al usuario
const SUGERENCIAS = [
  '🌿 Lago Sandoval y su biodiversidad',
  '🐒 Monos y fauna silvestre amazónica',
  '🛶 Paseos en bote por ríos amazónicos',
  '🌳 Reservas naturales y áreas protegidas',
  '🦜 Observación de aves tropicales',
  '🏡 Comunidades nativas y cultura local',
  '🌊 Cascadas y cuerpos de agua',
  '🌺 Flora medicinal de la selva',
]

/**
 * Componente principal de la aplicación AmazoníaSearch.
 * Gestiona todo el estado global, las llamadas a la API,
 * y la composición de la interfaz de usuario.
 */
export default function App() {
  // === Estado de la aplicación ===
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [systemInfo, setSystemInfo] = useState(null)
  const [searchTime, setSearchTime] = useState(null)
  const [totalResults, setTotalResults] = useState(0)
  const [modelName, setModelName] = useState('')
  const [hnswParams, setHnswParams] = useState(null)
  const [hasSearched, setHasSearched] = useState(false)

  // === Carga inicial de categorías e información del sistema ===
  useEffect(() => {
    // Obtener las categorías disponibles
    fetch(`${API_URL}/categories`)
      .then((res) => res.json())
      .then((data) => setCategories(data.categorias || []))
      .catch((err) => console.error('Error al cargar categorías:', err))

    // Obtener información del sistema
    fetch(`${API_URL}/`)
      .then((res) => res.json())
      .then((data) => setSystemInfo(data))
      .catch((err) => console.error('Error al cargar info del sistema:', err))
  }, [])

  // === Función principal de búsqueda semántica ===
  const handleSearch = useCallback(async ({ query: searchQuery, k, categoria }) => {
    if (!searchQuery.trim()) return

    setQuery(searchQuery)
    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const body = {
        query: searchQuery,
        k: k || 10,
        categoria: categoria || null,
      }

      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      setResults(data.resultados || [])
      setTotalResults(data.total_resultados || 0)
      setSearchTime(data.tiempo_busqueda_ms || 0)
      setModelName(data.modelo || '')
      setHnswParams(data.parametros_hnsw || null)
    } catch (err) {
      console.error('Error en la búsqueda:', err)
      setError(err.message || 'Ocurrió un error inesperado al realizar la búsqueda.')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }, [])

  // === Manejar clic en sugerencia ===
  const handleSuggestionClick = (suggestion) => {
    // Eliminar el emoji del inicio de la sugerencia
    const cleanQuery = suggestion.replace(/^[^\w\sáéíóúñ]+\s*/i, '')
    handleSearch({ query: cleanQuery, k: 10, categoria: null })
  }

  // === Reintentar búsqueda tras un error ===
  const handleRetry = () => {
    if (query) {
      handleSearch({ query, k: 10, categoria: selectedCategory })
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* === ORBES DECORATIVOS DE FONDO === */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0" aria-hidden="true">
        <div className="orb orb-emerald w-[600px] h-[600px] -top-48 -left-48 animate-pulse-glow" />
        <div
          className="orb orb-gold w-[400px] h-[400px] top-1/3 -right-32 animate-pulse-glow"
          style={{ animationDelay: '1.5s' }}
        />
        <div
          className="orb orb-teal w-[500px] h-[500px] -bottom-32 left-1/4 animate-pulse-glow"
          style={{ animationDelay: '3s' }}
        />
        <div
          className="orb orb-emerald w-[300px] h-[300px] top-2/3 right-1/4 animate-pulse-glow"
          style={{ animationDelay: '4.5s' }}
        />
      </div>

      {/* === CONTENIDO PRINCIPAL === */}
      <div className="relative z-10">
        {/* === SECCIÓN HERO / CABECERA === */}
        <header className="relative pt-12 pb-8 md:pt-20 md:pb-12">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            {/* Icono decorativo */}
            <div className="flex items-center justify-center gap-3 mb-6 animate-fade-in-up">
              <TreePine className="w-8 h-8 md:w-10 md:h-10 text-amazonia-400 animate-float" />
              <Leaf
                className="w-6 h-6 md:w-7 md:h-7 text-amazonia-500 animate-float"
                style={{ animationDelay: '1s' }}
              />
            </div>

            {/* Título principal con gradiente */}
            <h1
              className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-4 animate-fade-in-up text-gradient-hero"
              style={{ animationDelay: '0.1s' }}
            >
              AmazoníaSearch
            </h1>

            {/* Subtítulo descriptivo */}
            <p
              className="text-base sm:text-lg md:text-xl text-noche-400 max-w-2xl mx-auto leading-relaxed mb-10 animate-fade-in-up font-light"
              style={{ animationDelay: '0.2s' }}
            >
              Buscador Semántico Inteligente de Atractivos Turísticos
              <br className="hidden sm:block" />
              <span className="text-amazonia-400/80">de Puerto Maldonado</span>
            </p>

            {/* Barra de búsqueda */}
            <div className="animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <SearchBar
                onSearch={handleSearch}
                categories={categories}
                loading={loading}
              />
            </div>
          </div>
        </header>

        {/* === SECCIÓN DE RESULTADOS === */}
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          {/* Panel de estadísticas */}
          {hasSearched && !error && (results || loading) && (
            <div className="mb-8 animate-fade-in-up">
              <Stats
                searchTime={searchTime}
                totalResults={totalResults}
                model={modelName}
                hnswParams={hnswParams}
              />
            </div>
          )}

          {/* Mensaje de error */}
          {error && (
            <div className="animate-fade-in-up">
              <div className="glass rounded-2xl p-8 max-w-xl mx-auto text-center border border-red-500/20 bg-red-500/5">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
                  <span className="text-3xl">⚠️</span>
                </div>
                <h3 className="text-lg font-semibold text-red-400 mb-2">
                  Error en la búsqueda
                </h3>
                <p className="text-noche-400 text-sm mb-6">{error}</p>
                <button
                  onClick={handleRetry}
                  className="px-6 py-2.5 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 hover:border-red-500/30 transition-all duration-300 text-sm font-medium"
                >
                  Reintentar búsqueda
                </button>
              </div>
            </div>
          )}

          {/* Grilla de resultados o esqueletos de carga */}
          {hasSearched && !error && (
            <ResultsGrid results={results} loading={loading} />
          )}

          {/* Sugerencias iniciales (cuando no se ha buscado nada) */}
          {!hasSearched && !loading && (
            <div className="animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
              <div className="text-center mb-8">
                <p className="text-noche-500 text-sm font-medium uppercase tracking-widest mb-2">
                  Prueba con estas búsquedas
                </p>
                <div className="w-12 h-0.5 bg-gradient-to-r from-transparent via-amazonia-500/40 to-transparent mx-auto" />
              </div>

              <div className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
                {SUGERENCIAS.map((sugerencia, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestionClick(sugerencia)}
                    className="glass px-4 py-2.5 rounded-xl text-sm text-noche-300 hover:text-amazonia-300 hover:border-amazonia-500/30 hover:bg-amazonia-500/5 transition-all duration-300 cursor-pointer group"
                    style={{ animationDelay: `${0.6 + i * 0.05}s` }}
                  >
                    <span className="group-hover:scale-110 inline-block transition-transform duration-300">
                      {sugerencia}
                    </span>
                  </button>
                ))}
              </div>

              {/* Información del sistema */}
              {systemInfo && (
                <div className="mt-16 text-center animate-fade-in-up" style={{ animationDelay: '1s' }}>
                  <div className="glass rounded-2xl p-6 max-w-md mx-auto">
                    <p className="text-noche-500 text-xs uppercase tracking-widest mb-3">
                      Sistema activo
                    </p>
                    <p className="text-amazonia-400 text-sm font-medium">
                      {systemInfo.sistema || systemInfo.system || 'AmazoníaSearch API'}
                    </p>
                    {systemInfo.version && (
                      <p className="text-noche-600 text-xs mt-1">
                        Versión {systemInfo.version}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>

        {/* === PIE DE PÁGINA === */}
        <footer className="relative border-t border-white/5 py-8 mt-8">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              {/* Información del proyecto */}
              <div className="flex items-center gap-2 text-noche-600 text-sm">
                <TreePine className="w-4 h-4 text-amazonia-600" />
                <span>AmazoníaSearch</span>
                <span className="text-noche-700">•</span>
                <span>Búsqueda Semántica Vectorial</span>
              </div>

              {/* Curso académico */}
              <div className="flex items-center gap-2 text-noche-600 text-xs">
                <BookOpen className="w-3.5 h-3.5" />
                <span>Estructura de Datos y Algoritmos Avanzado</span>
              </div>

              {/* Enlace al repositorio */}
              <div className="flex items-center gap-3">
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-noche-600 hover:text-amazonia-400 transition-colors duration-300"
                  aria-label="Repositorio en GitHub"
                >
                  <Github className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
