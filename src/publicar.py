"""Fase 7 - Subir el vídeo a YouTube como PRIVADO para revisarlo antes de publicarlo.

Marca "Creado para niños", añade capítulos a la descripción, miniatura y subtítulos.

Requisitos (una sola vez):
  1. Google Cloud Console: activa "YouTube Data API v3" y crea credenciales OAuth
     de tipo "Aplicación de escritorio". Descarga el JSON como client_secret.json en la raíz.
  2. pip install google-auth-oauthlib
  La primera ejecución abre el navegador para autorizar tu canal; guarda token.json.

Uso:
  python src/publicar.py salida/videos/video01.mp4 guiones/video01_publicacion.yaml
  python src/publicar.py ... --simular      # solo muestra lo que subiría
"""
import argparse, json, os, sys
import yaml

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]  # force-ssl: subtítulos


def capitulos(meta, tiempos_json):
    """Capítulos de YouTube: el primero en 0:00, mínimo 3 y de al menos 10 s."""
    t = json.load(open(tiempos_json, encoding="utf-8"))["escenas"]
    marcas = sorted((t[k], v) for k, v in meta["capitulos"].items() if k in t)
    limpias = []
    for seg, titulo in marcas:
        if not limpias or seg - limpias[-1][0] >= 10:
            limpias.append((seg, titulo))
    if not limpias or limpias[0][0] != 0:
        limpias.insert(0, (0, "Inicio"))
    fmt = lambda s: f"{int(s//60)}:{int(s%60):02d}"
    return "\n".join(f"{fmt(s)} {titulo}" for s, titulo in limpias) if len(limpias) >= 3 else ""


def cuerpo(meta, tiempos_json):
    desc = meta["descripcion"].replace("{capitulos}", capitulos(meta, tiempos_json))
    if len(meta["titulo"]) > 100:
        sys.exit("El título supera 100 caracteres")
    return {
        "snippet": {"title": meta["titulo"], "description": desc[:5000], "tags": meta["etiquetas"],
                    "categoryId": meta["categoria"], "defaultLanguage": meta["idioma"],
                    "defaultAudioLanguage": meta["idioma"]},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": bool(meta["creado_para_ninos"]),
                   "containsSyntheticMedia": bool(meta["contenido_sintetico"]), "embeddable": True},
    }


def youtube():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    cred = Credentials.from_authorized_user_file("token.json", SCOPES) if os.path.exists("token.json") else None
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            cred = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES).run_local_server(port=0)
        open("token.json", "w").write(cred.to_json())
    return build("youtube", "v3", credentials=cred)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("metadatos")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()

    base = a.video[:-4]
    meta = yaml.safe_load(open(a.metadatos, encoding="utf-8"))
    body = cuerpo(meta, base + ".tiempos.json")
    if a.simular:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return

    from googleapiclient.http import MediaFileUpload
    yt = youtube()
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(a.video, chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        estado, resp = req.next_chunk()
        if estado:
            print(f"\r  subiendo {estado.progress()*100:.0f} %", end="", flush=True)
    vid = resp["id"]
    print(f"\n  subido: https://studio.youtube.com/video/{vid}/edit (PRIVADO)")

    mini = base + "_miniatura.png"
    if os.path.exists(mini):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(mini)).execute()
            print("  miniatura OK")
        except Exception as e:  # requiere canal verificado por teléfono
            print(f"  [aviso] miniatura no subida: {e}")
    if os.path.exists(base + ".srt"):
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": meta["idioma"],
                                                               "name": "Español", "isDraft": False}},
                             media_body=MediaFileUpload(base + ".srt")).execute()
        print("  subtítulos OK")
    print("  Revisa el vídeo en YouTube Studio y cámbialo a público cuando esté bien.")


if __name__ == "__main__":
    main()
