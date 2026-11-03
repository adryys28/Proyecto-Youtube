"""Paso 1 - Descubrir contenido con más tracción en un nicho.

Usa YouTube Data API v3 (cuota por defecto: 10.000 unidades/día;
search.list = 100 unidades, videos.list y channels.list = 1 unidad).

Métrica clave: 'outlier' = visualizaciones / suscriptores del canal.
Un vídeo con outlier alto funciona por el tema/gancho, no por el tamaño del canal.

Uso:
  python src/descubrir.py "inteligencia artificial" --region ES --idioma es --dias 30 --max 50
  python src/descubrir.py --tendencias --region ES
"""
import argparse, csv, os, sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()


def cliente():
    clave = os.getenv("YOUTUBE_API_KEY")
    if not clave:
        sys.exit("Falta YOUTUBE_API_KEY en .env")
    return build("youtube", "v3", developerKey=clave)


def buscar_ids(yt, consulta, region, idioma, dias, maximo):
    desde = (datetime.now(timezone.utc) - timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids, token = [], None
    while len(ids) < maximo:
        r = yt.search().list(
            q=consulta, part="id", type="video", order="viewCount",
            regionCode=region, relevanceLanguage=idioma, publishedAfter=desde,
            maxResults=min(50, maximo - len(ids)), pageToken=token,
        ).execute()
        ids += [i["id"]["videoId"] for i in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    return ids


def tendencias_ids(yt, region, maximo):
    r = yt.videos().list(part="id", chart="mostPopular", regionCode=region,
                         maxResults=min(50, maximo)).execute()
    return [i["id"] for i in r.get("items", [])]


def en_lotes(lista, n=50):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]


def detalles(yt, ids):
    videos = []
    for lote in en_lotes(ids):
        r = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(lote)).execute()
        videos += r.get("items", [])
    canales = {v["snippet"]["channelId"] for v in videos}
    subs = {}
    for lote in en_lotes(list(canales)):
        r = yt.channels().list(part="statistics", id=",".join(lote)).execute()
        for c in r.get("items", []):
            st = c["statistics"]
            subs[c["id"]] = 0 if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0))
    return videos, subs


def puntuar(videos, subs):
    ahora = datetime.now(timezone.utc)
    filas = []
    for v in videos:
        sn, st = v["snippet"], v.get("statistics", {})
        vistas = int(st.get("viewCount", 0))
        pub = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
        dias = max((ahora - pub).total_seconds() / 86400, 1)
        s = subs.get(sn["channelId"], 0)
        filas.append({
            "id": v["id"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "titulo": sn["title"],
            "canal": sn["channelTitle"],
            "publicado": sn["publishedAt"][:10],
            "duracion": v["contentDetails"]["duration"],
            "vistas": vistas,
            "vistas_dia": round(vistas / dias),
            "likes": int(st.get("likeCount", 0)),
            "comentarios": int(st.get("commentCount", 0)),
            "suscriptores": s,
            "outlier": round(vistas / s, 2) if s else "",
            "engagement_%": round(100 * (int(st.get("likeCount", 0)) + int(st.get("commentCount", 0))) / vistas, 2) if vistas else 0,
        })
    filas.sort(key=lambda f: (f["outlier"] or 0, f["vistas_dia"]), reverse=True)
    return filas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("consulta", nargs="?")
    p.add_argument("--tendencias", action="store_true", help="Usa el ranking 'mostPopular' de la región")
    p.add_argument("--region", default="ES")
    p.add_argument("--idioma", default="es")
    p.add_argument("--dias", type=int, default=30)
    p.add_argument("--max", type=int, default=50)
    p.add_argument("--salida", default="salida/descubrimiento.csv")
    a = p.parse_args()
    if not a.consulta and not a.tendencias:
        p.error("Indica una consulta o --tendencias")

    yt = cliente()
    ids = tendencias_ids(yt, a.region, a.max) if a.tendencias else \
        buscar_ids(yt, a.consulta, a.region, a.idioma, a.dias, a.max)
    filas = puntuar(*detalles(yt, ids))

    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: abre bien en Excel
        w = csv.DictWriter(f, fieldnames=filas[0].keys(), delimiter=";")
        w.writeheader(); w.writerows(filas)
    for f in filas[:10]:
        print(f"{f['outlier']!s:>8}  {f['vistas_dia']:>9}/día  {f['titulo'][:70]}")
    print(f"\n{len(filas)} vídeos -> {a.salida}")


if __name__ == "__main__":
    main()
