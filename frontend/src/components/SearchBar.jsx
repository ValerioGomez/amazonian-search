import { useState } from 'react'
import { Search, SlidersHorizontal, Loader2 } from 'lucide-react'

/**
 * Componente de barra de búsqueda con filtros.
 * Permite al usuario ingresar consultas semánticas,
 * filtrar por categoría y seleccionar el número de resultados.
 *
 * @param {Function} onSearch - Callback que recibe { query, k, categoria }
 * @param {string[]} categories - Lista de categorías disponibles
 * @param {boolean} loading - Si la búsqueda está en progreso
 */
export default function SearchBar({ onSearch, categories, loading }) {
  const [query, setQuery] = useState('')
  const [k, setK] = useState(10)
  const [categoria, setCategoria] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // Opciones de cantidad de resultados
  const kOptions = [5, 10, 15, 20]

  // Ejecutar búsqueda
  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!query.trim() || loading) return
    onSearch({
      query: query.trim(),
      k,
      categoria: categoria || null,
    })
  }

  // Buscar al presionar Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit()
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Contenedor principal con glassmorphism */}
      <div className="glass-strong rounded-2xl p-2 shadow-glow-sm hover:shadow-glow-md transition-shadow duration-500">
        {/* Fila de búsqueda */}
        <div className="flex items-center gap-2">
          {/* Campo de búsqueda */}
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-noche-500 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe lo que deseas explorar en la Amazonía..."
              className="w-full pl-12 pr-4 py-3.5 bg-transparent text-noche-200 placeholder-noche-600 text-sm md:text-base focus:outline-none focus:placeholder-noche-500 transition-colors duration-300 rounded-xl"
              disabled={loading}
              autoComplete="off"
              spellCheck="false"
            />
          </div>

          {/* Botón de filtros */}
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`p-3 rounded-xl transition-all duration-300 flex-shrink-0 ${
              showFilters
                ? 'bg-amazonia-500/15 text-amazonia-400 border border-amazonia-500/30'
                : 'text-noche-500 hover:text-noche-300 hover:bg-white/5 border border-transparent'
            }`}
            title="Mostrar filtros avanzados"
            aria-label="Alternar filtros avanzados"
          >
            <SlidersHorizontal className="w-5 h-5" />
          </button>

          {/* Botón de búsqueda */}
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || loading}
            className="flex items-center gap-2 px-5 md:px-7 py-3.5 rounded-xl bg-gradient-to-r from-amazonia-600 to-amazonia-500 text-white font-medium text-sm transition-all duration-300 hover:from-amazonia-500 hover:to-amazonia-400 hover:shadow-glow-md disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:shadow-none flex-shrink-0 active:scale-[0.97]"
            aria-label="Buscar"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="hidden md:inline">Buscando...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span className="hidden md:inline">Buscar</span>
              </>
            )}
          </button>
        </div>

        {/* Panel de filtros avanzados (expandible) */}
        <div
          className={`overflow-hidden transition-all duration-400 ease-in-out ${
            showFilters ? 'max-h-40 opacity-100 mt-2' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
            {/* Selector de categoría */}
            <div className="flex-1 w-full sm:w-auto">
              <label className="block text-[10px] uppercase tracking-widest text-noche-600 mb-1.5 font-medium">
                Categoría
              </label>
              <select
                value={categoria}
                onChange={(e) => setCategoria(e.target.value)}
                className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-noche-300 focus:outline-none focus:border-amazonia-500/40 focus:ring-1 focus:ring-amazonia-500/20 transition-all duration-300 appearance-none cursor-pointer"
                disabled={loading}
              >
                <option value="">Todas las categorías</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Selector de número de resultados */}
            <div className="w-full sm:w-auto">
              <label className="block text-[10px] uppercase tracking-widest text-noche-600 mb-1.5 font-medium">
                Resultados
              </label>
              <div className="flex gap-1.5">
                {kOptions.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setK(option)}
                    disabled={loading}
                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all duration-300 ${
                      k === option
                        ? 'bg-amazonia-500/20 text-amazonia-400 border border-amazonia-500/30'
                        : 'bg-white/[0.03] text-noche-500 border border-white/[0.06] hover:text-noche-300 hover:bg-white/[0.06]'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Indicador de filtros activos */}
      {(categoria || k !== 10) && (
        <div className="flex items-center justify-center gap-2 mt-3 animate-fade-in-up">
          {categoria && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amazonia-500/10 text-amazonia-400 text-xs border border-amazonia-500/20">
              {categoria}
              <button
                onClick={() => setCategoria('')}
                className="ml-0.5 hover:text-amazonia-300 transition-colors"
                aria-label={`Quitar filtro ${categoria}`}
              >
                ×
              </button>
            </span>
          )}
          {k !== 10 && (
            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-oro-500/10 text-oro-400 text-xs border border-oro-500/20">
              {k} resultados
            </span>
          )}
        </div>
      )}
    </div>
  )
}
