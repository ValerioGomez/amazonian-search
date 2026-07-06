import ResultCard from './ResultCard'
import { SearchX } from 'lucide-react'

/**
 * Componente de grilla de resultados.
 * Renderiza las tarjetas de resultados en una cuadrícula responsiva,
 * esqueletos de carga animados, o un mensaje de sin resultados.
 *
 * @param {Array|null} results - Lista de resultados de búsqueda
 * @param {boolean} loading - Si la búsqueda está en progreso
 */
export default function ResultsGrid({ results, loading }) {
  // === ESQUELETOS DE CARGA ===
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="glass rounded-2xl p-5 opacity-0 animate-fade-in-up"
            style={{ animationDelay: `${i * 0.08}s`, animationFillMode: 'forwards' }}
          >
            {/* Badge de similitud esqueleto */}
            <div className="absolute -top-3 -right-3 relative">
              <div className="w-14 h-14 rounded-full skeleton absolute -top-3 right-0" />
            </div>

            {/* Categoría esqueleto */}
            <div className="mb-3">
              <div className="h-5 w-24 rounded-full skeleton" />
            </div>

            {/* Título esqueleto */}
            <div className="h-6 w-3/4 rounded-lg skeleton mb-2" />

            {/* Descripción esqueleto - 3 líneas */}
            <div className="space-y-2 mb-4">
              <div className="h-3.5 w-full rounded skeleton" />
              <div className="h-3.5 w-full rounded skeleton" />
              <div className="h-3.5 w-2/3 rounded skeleton" />
            </div>

            {/* Ubicación esqueleto */}
            <div className="flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded-full skeleton" />
              <div className="h-3 w-40 rounded skeleton" />
            </div>

            {/* Coordenadas esqueleto */}
            <div className="mt-2">
              <div className="h-2.5 w-32 rounded skeleton" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  // === SIN RESULTADOS ===
  if (results && results.length === 0) {
    return (
      <div className="animate-fade-in-up">
        <div className="glass rounded-2xl p-12 text-center max-w-lg mx-auto">
          <div className="w-20 h-20 mx-auto mb-5 rounded-full bg-noche-800/50 flex items-center justify-center">
            <SearchX className="w-9 h-9 text-noche-600" />
          </div>
          <h3 className="text-lg font-semibold text-noche-300 mb-2">
            No se encontraron resultados
          </h3>
          <p className="text-noche-500 text-sm leading-relaxed">
            Intenta con otros términos de búsqueda o modifica los filtros
            para ampliar los resultados.
          </p>
        </div>
      </div>
    )
  }

  // === RESULTADOS ENCONTRADOS ===
  if (results && results.length > 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {results.map((attraction, index) => (
          <ResultCard
            key={attraction.id || index}
            attraction={attraction}
            index={index}
          />
        ))}
      </div>
    )
  }

  // === Estado nulo (no debería ocurrir normalmente) ===
  return null
}
