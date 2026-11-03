# Proyecto YouTube — canal de clips automatizado

Pipeline: **descubrir → detectar gancho → recortar → editar → publicar → medir**.

## Plan paso a paso

| # | Paso | Automatizable | Herramienta |
|---|------|---------------|-------------|
| 1 | Elegir nicho y fuente de contenido **con permiso** | No (decisión) | — |
| 2 | Descubrir vídeos con más tracción | Sí | `src/descubrir.py` (YouTube Data API v3) |
| 3 | Detectar el gancho (momento más repetido) | Sí | `src/ganchos.py` (heatmap vía yt-dlp) |
| 4 | Recortar y pasar a 9:16 | Sí | `src/recortar.py` (yt-dlp + ffmpeg) |
| 5 | Subtítulos, título del gancho en los 2 primeros s, comentario/valor propio | Parcial | Whisper + ffmpeg (siguiente fase) |
| 6 | Revisión humana y publicación programada | Parcial | YouTube Data API `videos.insert` |
| 7 | Medir retención y repetir lo que funciona | Sí | YouTube Analytics API |

### Riesgo principal: política de contenido
- **Contenido reutilizado**: clips de terceros sin aportación propia no se monetizan.
- **Contenido no auténtico** (renombrado el 15/07/2025): penaliza lo producido en masa con plantilla y poca variación. La sanción puede afectar al **canal entero**.
- Copyright: sin permiso del titular → reclamaciones de Content ID o avisos.

Fuentes de contenido viables: vídeos propios (podcast, directos), creadores con **programa de clipping** o permiso por escrito, o contenido con licencia CC BY.
Cada clip debe llevar valor añadido real (contexto, comentario, edición, montaje).

### Requisitos YPP (verificar en YouTube Studio > Ganar)
- Nivel 1 (fan funding): 500 suscriptores + 3 subidas en 90 días + 3.000 h en 365 días o 3 M vistas de Shorts en 90 días.
- Nivel 2 (anuncios): 1.000 suscriptores + 4.000 h en 12 meses o 10 M vistas de Shorts en 90 días.
- Fuentes de terceros anuncian que desde el 01/02/2027 pasa a 8.000 h o 20 M vistas de Shorts. **No verificado en la fuente oficial.**

## Uso

```bash
pip install -r requirements.txt          # requiere ffmpeg en el PATH
cp .env.example .env                       # rellena YOUTUBE_API_KEY

# 1. Descubrir (ordenado por outlier = vistas / suscriptores)
python src/descubrir.py "finanzas personales" --region ES --idioma es --dias 30
python src/descubrir.py --tendencias --region ES

# 2. Ganchos del vídeo elegido
python src/ganchos.py "https://www.youtube.com/watch?v=ID" --top 3 --duracion 45

# 3. Clips verticales
python src/recortar.py salida/ganchos/ID.json
```

Salidas en `salida/` (ignorada por git). El CSV usa `;` y UTF-8 con BOM para abrirlo directamente en Excel.

## Limitaciones conocidas
- El heatmap solo existe en vídeos con suficientes visualizaciones.
- El recorte 9:16 es central; si el sujeto no está centrado hace falta seguimiento de caras.
- Cuota API por defecto: 10.000 unidades/día; cada búsqueda cuesta 100.
