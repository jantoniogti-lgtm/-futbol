IPTV FÚTBOL V21 · ACTUALIZACIÓN AUTOMÁTICA COMPLETA

OBJETIVO
La página ya no depende de una lista fija de partidos. GitHub Actions reconstruye cada 30 minutos una ventana móvil de 7 días.

FUENTES
- Calendario y partidos: ESPN Soccer API pública, por competición, para evitar que falten partidos de una jornada.
- Televisión: Fútbol TV, que se consulta y se cruza con cada partido para obtener los canales españoles.
- Escudos: URLs de imágenes de Fútbol TV almacenadas en matches.json/logos.json.

COMPETICIONES INCLUIDAS EN EL ACTUALIZADOR
- LaLiga EA Sports
- Premier League
- Serie A Italia
- Bundesliga
- Ligue 1
- Liga Hypermotion
- Primera Federación
- Liga F
- Europa League
- Champions League
- Copa Libertadores
- Coppa Italia

FUNCIONAMIENTO
1. Cada 30 minutos GitHub Actions ejecuta update_matches.py.
2. Descarga todos los partidos de los próximos 7 días para las competiciones anteriores.
3. Consulta Fútbol TV y cruza fecha + hora + equipos para incorporar los canales de televisión.
4. update_logos.py reaplica los escudos.
5. Si hay cambios, GitHub hace commit y GitHub Pages muestra los datos nuevos.

IMPORTANTE
La página web nunca inventa partidos para completar una jornada. La fuente de calendario se reconstruye completa en cada ejecución. Si Fútbol TV no está disponible temporalmente, el calendario de partidos sigue actualizándose y conserva los canales de la versión anterior cuando coinciden.

FILTROS
- 7 días
- Competición
- Canal de TV
- Se pueden combinar competición + canal
