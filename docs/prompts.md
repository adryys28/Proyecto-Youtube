# Prompts para producir el canal con Claude

Úsalos en orden, en una sesión de Claude Code sobre este repositorio. Cada fase deja sus resultados en el repo para que la siguiente parta de ahí.

Limitación: Claude escribe guiones, letras, código y metadatos, y orquesta herramientas; **no genera audio, imagen ni vídeo por sí mismo**. Para eso hacen falta herramientas externas de voz, música e imagen (fase 4).

## 1. Investigación de mercado
```
Con src/descubrir.py y la YouTube Data API, analiza el nicho infantil en español e inglés
(canciones, aprendizaje de colores/números/animales, cuentos, rutinas de bebé).
Solo vídeos de más de 20 minutos publicados en los últimos 12 meses.
Entrégame en docs/investigacion.md: los 15 temas con mejor ratio vistas/suscriptores,
la duración media que funciona, patrones de títulos y miniaturas, y 5 huecos
(temas con demanda y poca oferta de calidad). Cita los datos, no supongas nada.
```

## 2. Concepto del canal
```
A partir de docs/investigacion.md, propón 3 conceptos de canal infantil 100 % original:
nombre, personajes propios, estilo visual, edad objetivo, propuesta educativa y
diferencia frente a los canales grandes. Comprueba que el nombre no está registrado
como marca en la EUIPO ni usado por otro canal relevante. Guárdalo en docs/concepto.md.
```

## 3. Repertorio legal
```
Hazme un catálogo de 30 canciones infantiles tradicionales en español e inglés que estén
en dominio público. Para cada una indica autor conocido o "anónimo", fecha, fuente que
lo acredita y nivel de riesgo (bajo/medio/alto). Descarta cualquiera con autor fallecido
hace menos de 80 años. Guárdalo en docs/repertorio.csv.
```

## 4. Herramientas de producción
```
Investiga herramientas actuales de voz sintética, música e imagen/animación con IA que
permitan uso comercial en YouTube, incluido contenido "Creado para niños".
Compara licencia (cita la cláusula), precio, calidad y si tienen API para automatizarlas.
Recomienda una combinación por menos de 50 €/mes. Guárdalo en docs/herramientas.md.
```

## 5. Guion del primer vídeo
```
Escribe el guion de un vídeo de 25 minutos para el concepto elegido: 6-8 segmentos
(canciones del repertorio + secciones educativas), gancho en los primeros 10 segundos,
transiciones entre segmentos y momentos de repetición/participación del niño.
Formato: tabla con tiempo, texto narrado, letra, descripción visual y prompt de imagen
para cada escena. Guárdalo en guiones/video01.md.
```

## 6. Automatizar la producción
```
Crea src/producir.py que, a partir de guiones/video01.md: genere las voces y músicas con
las APIs de docs/herramientas.md, genere o recoja las imágenes de cada escena, y monte el
vídeo final 1920x1080 con ffmpeg (animaciones simples, subtítulos, transiciones).
Claves en .env. Prueba cada paso y deja instrucciones en el README.
```

## 7. Publicación
```
Para guiones/video01.md genera: 5 títulos, descripción con capítulos y créditos,
etiquetas y 3 ideas de miniatura con su prompt. Crea src/publicar.py que suba el vídeo
con la YouTube Data API como privado, marcado "Creado para niños", con capítulos y
miniatura, para revisarlo yo antes de hacerlo público.
```

## 8. Medición y mejora
```
Con la YouTube Analytics API, analiza los vídeos publicados: retención por minuto,
puntos de abandono, CTR de miniatura y origen del tráfico. Compara con el guion
y dime qué segmentos cambiar en el próximo vídeo. Guárdalo en docs/informes/AAAA-MM.md.
```

## Consejos de uso
- Un prompt por fase; revisa el resultado antes de pasar a la siguiente.
- Si algo no te convence, pídelo concreto: "el gancho es flojo, dame 5 alternativas".
- Pide siempre fuentes en lo legal y en los datos.
