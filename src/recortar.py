"""Paso 3 - Descargar solo los tramos elegidos y pasarlos a vertical 9:16.

Entrada: el JSON generado por ganchos.py.
Salida: un MP4 1080x1920 por clip, listo para subtitular/editar.

Uso:
  python src/recortar.py salida/ganchos/VIDEO_ID.json
  python src/recortar.py salida/ganchos/VIDEO_ID.json --horizontal   # sin recorte 9:16
"""
import argparse, json, os, subprocess
import yt_dlp
from yt_dlp.utils import download_range_func


def descargar(url, ini, fin, destino):
    opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]",
        "merge_output_format": "mp4",
        "download_ranges": download_range_func(None, [(ini, fin)]),
        "force_keyframes_at_cuts": True,
        "outtmpl": destino,
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


def a_vertical(entrada, salida):
    # Recorte central 9:16. Para seguir a la persona habría que añadir detección de caras.
    vf = "crop='min(iw,ih*9/16)':ih,scale=1080:1920:flags=lanczos,setsar=1"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-vf", vf,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", salida], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("json_ganchos")
    p.add_argument("--horizontal", action="store_true")
    p.add_argument("--salida", default="salida/clips")
    a = p.parse_args()

    with open(a.json_ganchos, encoding="utf-8") as f:
        g = json.load(f)
    os.makedirs(a.salida, exist_ok=True)
    for n, c in enumerate(g["clips"], 1):
        bruto = os.path.join(a.salida, f"{g['id']}_{n}_bruto.mp4")
        final = os.path.join(a.salida, f"{g['id']}_{n}.mp4")
        descargar(g["url"], c["inicio"], c["fin"], bruto)
        if a.horizontal:
            os.replace(bruto, final)
        else:
            a_vertical(bruto, final)
            os.remove(bruto)
        print(f"-> {final}")


if __name__ == "__main__":
    main()
