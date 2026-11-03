# Proyecto YouTube — canal infantil de contenido propio

Pipeline: **analizar referentes → detectar ganchos → producir contenido propio → publicar → medir**.

## Plan paso a paso

| # | Paso | Automatizable | Herramienta |
|---|------|---------------|-------------|
| 1 | Nicho: infantil, vídeos largos, contenido propio | Hecho | — |
| 2 | Descubrir vídeos con más tracción | Sí | `src/descubrir.py` (YouTube Data API v3) |
| 3 | Analizar el gancho de los referentes (solo análisis) | Sí | `src/ganchos.py` (heatmap vía yt-dlp) |
| 4 | Producir el vídeo propio (guion, voz, animación, montaje) | Parcial | Siguiente fase |
| 5 | Subtítulos, título del gancho en los 2 primeros s, comentario/valor propio | Parcial | Whisper + ffmpeg (siguiente fase) |
| 6 | Revisión humana y publicación programada | Parcial | YouTube Data API `videos.insert` |
| 7 | Medir retención y repetir lo que funciona | Sí | YouTube Analytics API |

### Riesgo principal: política de contenido
- **Contenido reutilizado**: clips de terceros sin aportación propia no se monetizan.
- **Contenido no auténtico** (renombrado el 15/07/2025): penaliza lo producido en masa con plantilla y poca variación. La sanción puede afectar al **canal entero**.
- Copyright: sin permiso del titular → reclamaciones de Content ID o avisos.

Fuente de contenido elegida: **100 % propia** (ver abajo).
Cada clip debe llevar valor añadido real (contexto, comentario, edición, montaje).

### Requisitos YPP (verificar en YouTube Studio > Ganar)
- Nivel 1 (fan funding): 500 suscriptores + 3 subidas en 90 días + 3.000 h en 365 días o 3 M vistas de Shorts en 90 días.
- Nivel 2 (anuncios): 1.000 suscriptores + 4.000 h en 12 meses o 10 M vistas de Shorts en 90 días.
- Fuentes de terceros anuncian que desde el 01/02/2027 pasa a 8.000 h o 20 M vistas de Shorts. **No verificado en la fuente oficial.**

## Enfoque: contenido infantil 100 % propio (sin reutilizar vídeos ajenos)

Los vídeos de otros canales solo se **analizan** (temas, duración, ganchos). Nunca se descargan ni se reutilizan.

Reglas para evitar problemas legales:
- **Canciones**: solo letras y melodías de dominio público verificado (tradicionales anónimas) o propias. La grabación, el arreglo y la animación de otro canal están protegidos aunque la canción sea tradicional.
  - Dudosas: "The Wheels on the Bus" se atribuye a Verna Hills (1937-1939, fallecida en 1990): en la UE podría estar protegida hasta 2060.
  - "Baby Shark": el cántico es tradicional (Tribunal Supremo de Corea, 2025), pero la versión de Pinkfong es suya.
- **Personajes, nombres y estética**: propios. Nada que recuerde a Bebefinn, Cocomelon, Pinkfong, etc.
- **IA**: permitida si el resultado es original; declarar contenido sintético realista. Música/voz de IA solo con herramientas cuya licencia permita uso comercial.
- **"Creado para niños"**: marcar siempre (COPPA). Menos ingresos por anuncio; compensa con volumen de vídeos largos y otras vías (música en Spotify, merchandising propio).
- **Principios de calidad infantil**: contenido educativo y cuidado; nada producido en masa con plantilla.

## Uso

```bash
pip install -r requirements.txt          # requiere ffmpeg en el PATH
cp .env.example .env                       # rellena YOUTUBE_API_KEY

# 1. Descubrir (ordenado por outlier = vistas / suscriptores)
python src/descubrir.py "canciones infantiles" --duracion long --dias 365
python src/descubrir.py --tendencias --region ES

# 2. Ganchos de un vídeo de referencia (solo análisis, no descarga el vídeo)
python src/ganchos.py "https://www.youtube.com/watch?v=ID" --top 3 --duracion 45

```

Salidas en `salida/` (ignorada por git). El CSV usa `;` y UTF-8 con BOM para abrirlo directamente en Excel.

## Limitaciones conocidas
- El heatmap solo existe en vídeos con suficientes visualizaciones.
- Desde servidores en la nube YouTube puede pedir verificación antibots: ejecutar `ganchos.py` en local.
- Cuota API por defecto: 10.000 unidades/día; cada búsqueda cuesta 100.
