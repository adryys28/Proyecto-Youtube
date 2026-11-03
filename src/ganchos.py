"""Paso 2 - Detectar los ganchos (momentos más repetidos) de un vídeo.

Lee el 'heatmap' de "Lo más repetido" (Most Replayed) que expone yt-dlp:
100 segmentos con un valor normalizado 0-1. No todos los vídeos lo tienen
(YouTube solo lo muestra con volumen suficiente de visualizaciones).

Uso:
  python src/ganchos.py URL --top 3 --duracion 45
"""
import argparse, json, os, sys
import yt_dlp


def heatmap(url):
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    return info, info.get("heatmap") or []


def suavizar(valores, k=2):
    return [sum(valores[max(0, i - k):i + k + 1]) / len(valores[max(0, i - k):i + k + 1])
            for i in range(len(valores))]


def picos(hm, total, top, duracion, ignorar_inicio, umbral=0.5):
    """Devuelve las 'top' ventanas no solapadas centradas en los picos."""
    vals = suavizar([s["value"] for s in hm])
    orden = sorted(range(len(hm)), key=lambda i: vals[i], reverse=True)
    elegidos, maximo = [], None
    for i in orden:
        centro = (hm[i]["start_time"] + hm[i]["end_time"]) / 2
        if centro < total * ignorar_inicio:  # el arranque siempre sale alto: no es un gancho
            continue
        maximo = maximo or vals[i]
        if vals[i] < maximo * umbral:  # descarta picos débiles respecto al principal
            break
        ini = max(0.0, centro - duracion / 2)
        fin = min(total, ini + duracion)
        ini = max(0.0, fin - duracion)
        if all(fin <= e["inicio"] or ini >= e["fin"] for e in elegidos):
            elegidos.append({"inicio": round(ini, 1), "fin": round(fin, 1),
                             "intensidad": round(vals[i], 3)})
        if len(elegidos) == top:
            break
    return sorted(elegidos, key=lambda e: e["inicio"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--duracion", type=float, default=45, help="Segundos por clip")
    p.add_argument("--ignorar-inicio", type=float, default=0.03, help="Fracción inicial a descartar")
    p.add_argument("--umbral", type=float, default=0.5, help="Intensidad mínima relativa al pico principal")
    p.add_argument("--forzar", action="store_true", help="Ignora la comprobación de licencia CC")
    p.add_argument("--salida", default="salida/ganchos")
    a = p.parse_args()

    info, hm = heatmap(a.url)
    lic = info.get("license") or ""
    if "Creative Commons" not in lic and not a.forzar:
        sys.exit(f"Licencia no CC ('{lic or 'estándar'}'). Usa --forzar solo si tienes permiso escrito.")
    if not hm:
        sys.exit("Este vídeo no tiene datos de 'Lo más repetido'.")
    res = {"id": info["id"], "titulo": info["title"], "url": a.url,
           "canal": info.get("channel"), "canal_url": info.get("channel_url"), "licencia": lic,
           "duracion": info["duration"],
           "clips": picos(hm, info["duration"], a.top, a.duracion, a.ignorar_inicio, a.umbral)}

    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, f"{info['id']}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    for c in res["clips"]:
        print(f"{c['inicio']:>7}s - {c['fin']:>7}s  intensidad {c['intensidad']}")
    with open(os.path.join(a.salida, f"{info['id']}_atribucion.txt"), "w", encoding="utf-8") as f:
        titulo, canal = info["title"], info.get("channel")
        f.write(f'Contenido original: "{titulo}" de {canal} ({a.url}), '
                "licencia Creative Commons Atribución (CC BY).\n")
    print(f"-> {ruta}")


if __name__ == "__main__":
    main()
