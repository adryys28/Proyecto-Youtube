"""Fase 8 - Medir resultados con YouTube Analytics API y generar un informe mensual.

Para cada vídeo del canal: vistas, minutos vistos, % medio visto, suscriptores ganados,
curva de retención (puntos de abandono) y fuentes de tráfico. Cruza la retención con
los tiempos de escena del guion para decir QUÉ escena pierde audiencia.

Requisitos: activar "YouTube Analytics API" en Google Cloud (mismo client_secret.json que publicar.py).
Uso:
  python src/medir.py --desde 2026-11-01 --hasta 2026-11-30
  python src/medir.py --video VIDEO_ID --tiempos salida/videos/video01.tiempos.json
"""
import argparse, json, os
from datetime import date

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/youtube.readonly"]


def clientes():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    f = "token_analytics.json"
    cred = Credentials.from_authorized_user_file(f, SCOPES) if os.path.exists(f) else None
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            cred = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES).run_local_server(port=0)
        open(f, "w").write(cred.to_json())
    return build("youtubeAnalytics", "v2", credentials=cred), build("youtube", "v3", credentials=cred)


def consulta(ya, **kw):
    r = ya.reports().query(ids="channel==MINE", **kw).execute()
    cols = [c["name"] for c in r.get("columnHeaders", [])]
    return [dict(zip(cols, fila)) for fila in r.get("rows", [])]


def abandonos(curva, n=3):
    """Las n mayores caídas de retención entre puntos consecutivos."""
    caidas = [(curva[i]["audienceWatchRatio"] - curva[i + 1]["audienceWatchRatio"], curva[i + 1]["elapsedVideoTimeRatio"])
              for i in range(len(curva) - 1)]
    return sorted(caidas, reverse=True)[:n]


def escena_en(segundo, tiempos):
    actual = None
    for esc, t in sorted(tiempos["escenas"].items(), key=lambda x: x[1]):
        if t <= segundo:
            actual = esc
    return actual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default=date.today().replace(day=1).isoformat())
    ap.add_argument("--hasta", default=date.today().isoformat())
    ap.add_argument("--video", help="ID de un vídeo para el análisis de retención")
    ap.add_argument("--tiempos", help="tiempos.json generado por producir.py para ese vídeo")
    ap.add_argument("--salida", default="docs/informes")
    a = ap.parse_args()

    ya, yt = clientes()
    rango = dict(startDate=a.desde, endDate=a.hasta)
    L = [f"# Informe {a.desde} → {a.hasta}\n"]

    filas = consulta(ya, **rango, dimensions="video", sort="-views", maxResults=50,
                     metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained")
    titulos = {}
    if filas:
        r = yt.videos().list(part="snippet", id=",".join(f["video"] for f in filas)).execute()
        titulos = {v["id"]: v["snippet"]["title"] for v in r.get("items", [])}
    L += ["## Vídeos\n", "| Vídeo | Vistas | Min. vistos | Duración media | % visto | Subs |", "|---|---:|---:|---:|---:|---:|"]
    for f in filas:
        L.append(f"| {titulos.get(f['video'], f['video'])[:60]} | {f['views']} | {f['estimatedMinutesWatched']} | "
                 f"{f['averageViewDuration']//60}:{f['averageViewDuration']%60:02d} | {f['averageViewPercentage']:.1f} % | {f['subscribersGained']} |")

    L += ["\n## Fuentes de tráfico\n", "| Fuente | Vistas |", "|---|---:|"]
    for f in consulta(ya, **rango, dimensions="insightTrafficSourceType", metrics="views", sort="-views"):
        L.append(f"| {f['insightTrafficSourceType']} | {f['views']} |")

    vid = a.video or (filas[0]["video"] if filas else None)
    if vid:
        curva = consulta(ya, **rango, dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}",
                         metrics="audienceWatchRatio,relativeRetentionPerformance")
        if curva:
            dur = json.load(open(a.tiempos))["duracion"] if a.tiempos else None
            tiempos = json.load(open(a.tiempos)) if a.tiempos else None
            L += [f"\n## Retención: {titulos.get(vid, vid)}\n",
                  f"- Retención al 10 %: {curva[min(9, len(curva)-1)]['audienceWatchRatio']:.0%}",
                  f"- Retención al 50 %: {curva[min(49, len(curva)-1)]['audienceWatchRatio']:.0%}",
                  "\n### Mayores puntos de abandono\n"]
            for caida, pos in abandonos(curva):
                extra = ""
                if dur:
                    s = pos * dur
                    extra = f" → {int(s//60)}:{int(s%60):02d}, escena `{escena_en(s, tiempos)}`"
                L.append(f"- Caída de {caida:.1%} en el {pos:.0%} del vídeo{extra}")

    try:  # métricas de impresiones: su disponibilidad en la API no está verificada
        imp = consulta(ya, **rango, dimensions="video", metrics="videoThumbnailImpressions,videoThumbnailImpressionsClickRate",
                       sort="-videoThumbnailImpressions", maxResults=10)
        L += ["\n## Impresiones y CTR\n", "| Vídeo | Impresiones | CTR |", "|---|---:|---:|"]
        L += [f"| {titulos.get(f['video'], f['video'])[:60]} | {f['videoThumbnailImpressions']} | "
              f"{f['videoThumbnailImpressionsClickRate']:.1%} |" for f in imp]
    except Exception:
        L.append("\n_Impresiones y CTR no disponibles por API: consúltalos en YouTube Studio > Estadísticas > Alcance._")

    L += ["\n## Siguiente paso",
          "Pega este informe a Claude con el guion del próximo vídeo y pídele que ajuste las escenas con más abandono."]
    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, f"{a.desde[:7]}.md")
    open(ruta, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("->", ruta)


if __name__ == "__main__":
    main()
