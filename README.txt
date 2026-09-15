IPTV FÚTBOL V12 — AUTOMÁTICO CON FÚTBOL TV

SUBE TODO EL CONTENIDO DEL ZIP A TU REPOSITORIO, MANTENIENDO:
.github/workflows/update-futboltv.yml

Funcionamiento:
1. GitHub Actions descarga Fútbol TV cada 15 minutos.
2. Extrae los partidos de HOY + 6 días.
3. Extrae hora, competición, local, visitante y canales.
4. Regenera matches.json.
5. GitHub Pages muestra los nuevos datos.

La primera ejecución se puede lanzar manualmente desde:
GitHub > Actions > Actualizar partidos de Fútbol TV > Run workflow

La web no usa tu M3U/EPG privado.
Fuente: https://www.futboltv.info/

V13: se han eliminado los textos 'PRÓXIMO' y el reloj; los escudos tienen fallback visual para que nunca quede un hueco vacío. El parser no publica una actualización si extrae menos de 15 partidos.
