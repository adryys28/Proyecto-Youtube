# Fase 1 — Investigación del nicho infantil (vídeos largos)

**Fecha:** 03/11/2026 · **Muestra:** 401 vídeos únicos de más de 20 min publicados en 2026, los más vistos de 23 búsquedas en español e inglés.
**Datos en bruto:** `datos/investigacion_2026-11-03.csv`

## Limitaciones
- Sin clave de API: no hay datos de suscriptores, así que **no se calcula el ratio vistas/suscriptores** (outlier). Pendiente cuando haya `YOUTUBE_API_KEY`.
- Resultados de búsqueda de YouTube desde un servidor en la nube: pueden diferir de lo que ve un usuario en España.
- "Publicado en 2026" según el filtro de YouTube; las vistas son acumuladas a fecha de consulta.

## 1. Demanda por tema (mediana de vistas del top 20-30)

| Tema | Mediana | Canales distintos | Lectura |
|---|---:|---:|---|
| Dinosaurios para niños | 17,4 M | 12 | Mucha demanda, dominado por canales de familias reales |
| Baby songs (EN) | 16,3 M | 8 de 10 | Muy competido |
| Nursery rhymes (EN) | 13,3 M | 7 de 10 | Muy competido |
| Learn colors (EN) | 11,0 M | 7 de 10 | Muy competido |
| Cuentos infantiles | 8,0 M | 9 de 10 | Dominado por marcas (Peppa, Masha, Oddbods) |
| Canciones infantiles | 7,9 M | 8 de 10 | BabyBus, Plim Plim |
| Canciones para bebés | 6,2 M | 9 de 10 | — |
| Animales para niños | 5,6 M | 6 de 10 | — |
| Aprender colores | 5,0 M | 7 de 10 | — |
| Estimulación bebés | 4,4 M | 7 de 10 | — |
| Learn to talk (EN) | 3,6 M | 13 de 20 | Ms Rachel lidera |
| **Primeras palabras bebés** | **3,0 M** | **6 de 20** | **Un solo canal (Aprende Peque) tiene 10 de 20** |
| **Aprender a hablar bebés** | **3,0 M** | **9 de 20** | **Concentrado en 2 canales** |
| Aprender números | 2,5 M | 6 de 10 | Aprende Peque tiene 11 de 30 |
| Bedtime songs (EN) | 2,7 M | 9 de 10 | — |
| Rutinas con canciones | 2,0 M | 14 de 20 | Fragmentado, demanda media |
| Canciones de cuna | 1,9 M | 10 de 10 | Vídeos de 2 h, poca vista por vídeo |
| Formas | 1,0 M | 15 de 20 | Demanda baja |
| Vídeo sensorial bebé (ES) | 0,7 M | 13 de 20 | Demanda baja en español |
| Lavarse los dientes | 0,3 M | 15 de 20 | Demanda baja |

## 2. Duración

| Duración | Vídeos | Mediana de vistas |
|---|---:|---:|
| 20-30 min | 105 | 6,8 M |
| 30-45 min | 71 | 6,5 M |
| 45-65 min | 66 | 5,0 M |
| 65-130 min | 36 | 2,7 M |
| > 130 min | 27 | 2,0 M |

**Conclusión:** el punto óptimo está en **20-45 min**. Los vídeos de más de 1 h rinden menos por vídeo.

## 3. Patrones de título (305 vídeos con datos)
- 64 % usa `|` para separar tema y marca/serie.
- 44 % lleva emoji.
- 19 % indica la duración ("1 hora", "30 min").
- 15 % indica recopilación ("+More", "y más").
- Longitud media: 81 caracteres.
- Palabras más frecuentes: kids, songs, canciones, nursery rhymes, learn/aprende, baby/bebé, colores, animales, granja, números, dormir.

Plantilla que encaja con los datos: `Tema principal + beneficio | Serie o personaje 🎵 (duración)`
Ejemplo: `Primeras palabras para bebés: animales de la granja | [Personaje] 🐮 (30 min)`

## 4. Formatos que dominan
1. **Persona real enseñando a hablar** (Ms Rachel): los 4 vídeos más vistos de toda la muestra (53-123 M).
2. **Animación 3D de canciones** (BabyBus, Funny Lala, Eli Kids, Bebefinn).
3. **Series con marca** (Peppa, Bluey, Masha): no competible.
4. **Familias reales / juguetes** (Vlad y Niki, Kids Roma, Nastya): requieren niños en pantalla. No recomendado: implicaciones legales con menores.

## 5. Huecos detectados (demanda con poca competencia en español)
1. **Primeras palabras / aprender a hablar en español** (ojo: existe *Cantando Aprendo a Hablar*, 4,19 M de suscriptores, que no aparece entre los vídeos largos de 2026 de la muestra; hay que diferenciarse): ~3 M de mediana y solo 6-9 canales, uno dominante. En la muestra no aparece un equivalente en español de Ms Rachel con contenido original.
2. **Animales + vocabulario**: combina el tema más fuerte (animales/dinosaurios) con aprendizaje de palabras.
3. **Rutinas con canciones** (dormir, comer, bañarse): mercado fragmentado (14 canales en 20 resultados); nadie domina.
4. **Números en español**: un único canal concentra un tercio del top.
5. **Español de España**: por los nombres de canal y títulos, la mayoría del top en español apunta a Latinoamérica (no verificado vídeo a vídeo). Posible hueco para acento de España; mercado menor.

## Recomendación para la fase 2
Canal en español de **primeras palabras y aprendizaje del lenguaje (1-3 años)**, con animación propia, vídeos de 25-35 min y temas de alta demanda (animales, colores, rutinas) como vehículo del vocabulario.
