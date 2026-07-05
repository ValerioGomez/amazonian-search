import { Clock, Hash, Cpu, Layers, Zap } from 'lucide-react'

/**
 * Componente de panel de estadísticas de la búsqueda.
 * Muestra métricas clave como tiempo, resultados, modelo y parámetros HNSW.
 *
 * @param {number} searchTime - Tiempo de búsqueda en milisegundos
 * @param {number} totalResults - Total de resultados encontrados
 * @param {string} model - Nombre del modelo de embeddings
 * @param {Object|null} hnswParams - Parámetros del índice HNSW (M, ef_search, etc.)
 */
export default function Stats({ searchTime, totalResults, model, hnswParams }) {
  // Si no hay datos, no renderizar nada
  if (searchTime === null && !totalResults && !model) return null

  // Configuración de cada métrica a mostrar
  const estadisticas = [
    {
      icono: Clock,
      etiqueta: 'Tiempo',
      valor: searchTime !== null ? `${Number(searchTime).toFixed(1)} ms` : '—',
      color: 'text-amazonia-400',
      bgColor: 'bg-amazonia-500/10',
    },
    {
      icono: Hash,
      etiqueta: 'Resultados',
      valor: totalResults !== undefined ? totalResults.toString() : '—',
      color: 'text-selva-400',
      bgColor: 'bg-selva-500/10',
    },
    {
      icono: Cpu,
      etiqueta: 'Modelo',
      valor: model || '—',
      color: 'text-violet-400',
      bgColor: 'bg-violet-500/10',
      truncate: true,
    },
    {
      icono: Layers,
      etiqueta: 'HNSW M',
      valor: hnswParams?.M !== undefined ? hnswParams.M.toString() : '—',
      color: 'text-oro-400',
      bgColor: 'bg-oro-500/10',
    },
    {
      icono: Zap,
      etiqueta: 'ef_search',
      valor: hnswParams?.ef_search !== undefined ? hnswParams.ef_search.toString() : '—',
      color: 'text-sky-400',
      bgColor: 'bg-sky-500/10',
    },
  ]

  return (
    <div className="glass rounded-2xl p-3 sm:p-4 animate-slide-in-right">
      <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
        {estadisticas.map((stat, i) => {
          const Icon = stat.icono
          return (
            <div
              key={i}
              className="flex items-center gap-2.5 px-3 sm:px-4 py-2.5 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-white/[0.1] hover:bg-white/[0.04] transition-all duration-300 group"
            >
              {/* Icono con fondo coloreado */}
              <div
                className={`w-8 h-8 rounded-lg ${stat.bgColor} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}
              >
                <Icon className={`w-4 h-4 ${stat.color}`} />
              </div>

              {/* Etiqueta y valor */}
              <div className="min-w-0">
                <p className="text-[9px] uppercase tracking-widest text-noche-600 font-medium leading-none mb-0.5">
                  {stat.etiqueta}
                </p>
                <p
                  className={`text-xs sm:text-sm font-semibold text-noche-200 leading-none ${
                    stat.truncate ? 'max-w-[120px] truncate' : ''
                  }`}
                  title={stat.truncate ? stat.valor : undefined}
                >
                  {stat.valor}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
