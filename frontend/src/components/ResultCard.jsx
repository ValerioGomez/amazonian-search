import { MapPin, ExternalLink } from 'lucide-react'

/**
 * Componente de tarjeta individual de resultado.
 * Muestra la información de un atractivo turístico
 * con su porcentaje de similitud semántica.
 *
 * @param {Object} attraction - Datos del atractivo turístico
 * @param {number} index - Índice para animación escalonada
 */
export default function ResultCard({ attraction, index }) {
  const {
    nombre,
    categoria,
    descripcion,
    ubicacion,
    latitud,
    longitud,
    similitud,
  } = attraction

  // Calcular porcentaje de similitud
  const porcentaje = Math.round((similitud || 0) * 100)

  // Determinar el color del badge según el porcentaje de similitud
  const getBadgeStyles = () => {
    if (porcentaje >= 80) {
      return {
        bg: 'bg-gradient-to-br from-emerald-400 to-emerald-600',
        ring: 'ring-emerald-400/30',
        glow: 'shadow-[0_0_15px_rgba(52,211,153,0.3)]',
      }
    }
    if (porcentaje >= 60) {
      return {
        bg: 'bg-gradient-to-br from-amber-400 to-amber-600',
        ring: 'ring-amber-400/30',
        glow: 'shadow-[0_0_15px_rgba(251,191,36,0.3)]',
      }
    }
    return {
      bg: 'bg-gradient-to-br from-rose-400 to-rose-600',
      ring: 'ring-rose-400/30',
      glow: 'shadow-[0_0_15px_rgba(251,113,133,0.3)]',
    }
  }

  const badgeStyles = getBadgeStyles()

  // Mapear categorías a colores de pills
  const getCategoryColor = () => {
    const cat = (categoria || '').toLowerCase()
    if (cat.includes('natural') || cat.includes('reserva') || cat.includes('lago')) {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    }
    if (cat.includes('cultural') || cat.includes('comunidad')) {
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    }
    if (cat.includes('aventura') || cat.includes('deporte')) {
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20'
    }
    if (cat.includes('gastron') || cat.includes('comida')) {
      return 'bg-orange-500/10 text-orange-400 border-orange-500/20'
    }
    return 'bg-violet-500/10 text-violet-400 border-violet-500/20'
  }

  // Generar enlace a Google Maps si hay coordenadas
  const googleMapsUrl =
    latitud && longitud
      ? `https://www.google.com/maps?q=${latitud},${longitud}`
      : null

  return (
    <div
      className="group relative glass rounded-2xl p-5 card-glow hover:bg-white/[0.05] transition-all duration-500 hover:scale-[1.02] hover:-translate-y-1 opacity-0 animate-fade-in-up"
      style={{ animationDelay: `${index * 0.08}s`, animationFillMode: 'forwards' }}
    >
      {/* Badge de similitud - esquina superior derecha */}
      <div className="absolute -top-3 -right-3 z-10">
        <div
          className={`w-14 h-14 rounded-full ${badgeStyles.bg} ${badgeStyles.glow} ring-4 ${badgeStyles.ring} flex items-center justify-center transition-transform duration-300 group-hover:scale-110`}
        >
          <div className="text-center">
            <span className="block text-sm font-bold text-white leading-none">
              {porcentaje}
            </span>
            <span className="block text-[8px] font-medium text-white/80 leading-none mt-0.5">
              %
            </span>
          </div>
        </div>
      </div>

      {/* Etiqueta de categoría */}
      {categoria && (
        <div className="mb-3">
          <span
            className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] uppercase tracking-widest font-semibold border ${getCategoryColor()}`}
          >
            {categoria}
          </span>
        </div>
      )}

      {/* Nombre del atractivo */}
      <h3 className="text-lg font-bold text-noche-100 mb-2 pr-10 leading-snug group-hover:text-amazonia-300 transition-colors duration-300">
        {nombre}
      </h3>

      {/* Descripción (máximo 3 líneas con elipsis) */}
      {descripcion && (
        <p className="text-sm text-noche-400 leading-relaxed mb-4 line-clamp-3">
          {descripcion}
        </p>
      )}

      {/* Información de ubicación */}
      <div className="mt-auto space-y-2">
        {ubicacion && (
          <div className="flex items-start gap-2">
            <MapPin className="w-3.5 h-3.5 text-amazonia-500 mt-0.5 flex-shrink-0" />
            <span className="text-xs text-noche-500 leading-snug">{ubicacion}</span>
          </div>
        )}

        {/* Coordenadas y enlace a mapa */}
        {latitud && longitud && (
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-noche-700 font-mono">
              {Number(latitud).toFixed(5)}°, {Number(longitud).toFixed(5)}°
            </span>
            {googleMapsUrl && (
              <a
                href={googleMapsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-[10px] text-noche-600 hover:text-amazonia-400 transition-colors duration-300"
                title="Ver en Google Maps"
              >
                <ExternalLink className="w-3 h-3" />
                <span>Mapa</span>
              </a>
            )}
          </div>
        )}
      </div>

      {/* Línea decorativa inferior con gradiente */}
      <div className="absolute bottom-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-amazonia-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    </div>
  )
}
