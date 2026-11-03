# Fase 4 — Herramientas gratuitas con uso comercial

Criterio: **coste 0 €**, licencia que permita monetizar en YouTube y, si es posible, funcionamiento en CPU (sin tarjeta gráfica) para automatizarlo todo.

## Pila elegida

| Función | Herramienta | Licencia | Verificación | Notas |
|---|---|---|---|---|
| Personajes, fondos, miniaturas | **SVG generado por código** (lo dibuja Claude) + `rsvg-convert` / CairoSVG | Obra propia · LGPL (CairoSVG) | — | 100 % original, sin riesgo de licencia, funciona en CPU. Encaja con el estilo 2D plano del concepto |
| Animación | Python (transformaciones sobre SVG: rebote, parpadeo, entrada/salida) | Propio | — | Animación sencilla; suficiente para 1-3 años |
| Voz narrada | **Kokoro-82M** | Apache 2.0 (pesos y código) | Comprobado en el LICENSE del repo y en PyPI (v0.9.4) | Soporta español (`'e'`). Funciona en CPU |
| Música | Partituras escritas por código (**mido**) + **FluidSynth** + soundfont **FluidR3_GM** | MIT · LGPL · MIT | mido: PyPI. FluidR3: paquetes Debian/Mageia | Arreglos propios de melodías del repertorio |
| Canto | **Tu voz** (grabada con el móvil) o melodía instrumental con letra en pantalla | Propia | — | Kokoro habla, no canta. No he encontrado síntesis de canto gratuita con licencia comercial clara |
| Montaje | **ffmpeg** + **MoviePy** | LGPL/GPL · MIT | MoviePy: PyPI (v2.2.1) | La licencia del programa no afecta al vídeo resultante |
| Subtítulos | Generados desde el guion | Propio | — | Whisper (MIT) solo si se graba voz humana sin guion exacto |
| Tipografía | Google Fonts con licencia OFL (p. ej. Nunito, Baloo 2) | OFL | Pendiente comprobar cada fuente | Uso comercial permitido por la OFL |
| Edición manual (opcional) | DaVinci Resolve (gratis) o Kdenlive | Propietaria gratuita · GPL | Resolve: respuesta del soporte de Blackmagic en su foro | Para retoques fuera del flujo automático |

## Opcional si tienes tarjeta gráfica
| Herramienta | Licencia | Notas |
|---|---|---|
| FLUX.1 [schnell] (imágenes) | Apache 2.0 según las fichas del modelo; ficha oficial no consultable desde aquí | Requiere GPU con bastante memoria; en CPU no es viable. Ojo: **FLUX.1 [dev] no permite uso comercial gratis** |

## Descartadas
| Herramienta | Motivo |
|---|---|
| ElevenLabs (plan gratuito) | Uso no comercial según fuentes de terceros; uso comercial desde el plan de pago |
| Coqui XTTS-v2 | Pesos bajo licencia CPML: solo uso no comercial; la empresa ya no existe para vender licencias |
| Suno (plan gratuito) | No he podido verificar sus condiciones: no usar hasta comprobarlo |
| Voces Piper en español | Licencia de cada voz no verificable desde aquí (la de davefx usa datos CC0 pero parte de una voz inglesa cuya licencia no he comprobado) |
| Biblioteca de audio de YouTube | Válida para vídeos monetizados, pero algunas pistas exigen atribución y Content ID puede reclamar igualmente. Se deja como reserva |

## Requisitos para ejecutarlo
- Python 3.10+, ffmpeg, FluidSynth y el soundfont FluidR3_GM (`apt install fluidsynth fluid-soundfont-gm` en Debian/Ubuntu).
- Kokoro descarga sus pesos desde Hugging Face. Ese dominio está bloqueado en este entorno: hay que añadir `huggingface.co` y `*.hf.co` a los dominios permitidos o ejecutarlo en tu PC.

## Coste total: 0 €
