IPTV FÚTBOL — V22 CALENDARIO COMPLETO

Corrección principal:
- LaLiga se refuerza con una capa de seguridad para no perder partidos futuros si una API externa omite algún encuentro.
- Sábado 19/09/2026 incluye los 4 partidos de LaLiga: Osasuna-Rayo, Athletic-Alavés, Celta-Racing y Sevilla-Barcelona.
- Domingo 20/09/2026 incluye los 5 partidos de LaLiga.
- El actualizador obtiene los partidos de varias competiciones y usa Fútbol TV para asociar canales.
- Se mejoró el lector de Fútbol TV para mantener correctamente la fecha al recorrer la página.
- Los escudos se regeneran automáticamente desde logos.json.

GitHub Actions:
- update_matches.py cada 30 minutos.
- update_logos.py después de cada actualización.

Importante: el calendario de partidos se obtiene de fuentes públicas de resultados/calendario; Fútbol TV se usa para programación de canales. No se utilizan listas M3U ni datos IPTV privados.
