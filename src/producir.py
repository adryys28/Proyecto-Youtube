"""Fase 6 - Producir un vídeo completo a partir de un guion YAML.

Flujo: guion -> voces (Kokoro o espeak-ng) + música (MIDI + FluidSynth)
       -> planos animados (SVG -> PNG -> ffmpeg) -> vídeo final + subtítulos.

Uso:
  python src/producir.py guiones/video01.yaml                    # vídeo completo 1080p
  python src/producir.py guiones/video01.yaml --limite 6 --ancho 960   # prueba rápida
  python src/producir.py guiones/video01.yaml --voz espeak       # sin Kokoro

Requisitos: ffmpeg, rsvg-convert, fluidsynth + /usr/share/sounds/sf2/FluidR3_GM.sf2,
            pip install pyyaml mido  (y opcionalmente kokoro soundfile)
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, wave
import yaml, mido

sys.path.insert(0, os.path.dirname(__file__))
import dibujos as D

AR = 24000          # frecuencia de muestreo de todo el audio
FPS = 25
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"Falló: {' '.join(map(str, cmd[:6]))}...\n{r.stderr[-1500:]}")
    return r


def h(*partes):
    return hashlib.md5(json.dumps(partes, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


# ---------------- audio ----------------
def a_formato(entrada, salida, filtro=None):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", entrada]
    if filtro:
        cmd += ["-af", filtro]
    run(cmd + ["-ac", "1", "-ar", str(AR), "-sample_fmt", "s16", salida])


def silencio(seg, salida):
    with wave.open(salida, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(AR)
        w.writeframes(b"\0\0" * int(seg * AR))
    return salida


def duracion(wav):
    with wave.open(wav) as w:
        return w.getnframes() / AR


def unir_wav(lista, salida, total=None):
    """Concatena WAV del mismo formato. Si se da 'total', recorta o rellena a esa duración."""
    datos = b""
    for f in lista:
        with wave.open(f) as w:
            datos += w.readframes(w.getnframes())
    if total is not None:
        n = int(round(total * AR)) * 2
        datos = datos[:n] + b"\0" * max(0, n - len(datos))
    with wave.open(salida, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(AR)
        w.writeframes(datos)
    return salida


class Voz:
    """Kokoro (Apache 2.0) si está disponible; si no, espeak-ng."""
    VOCES_KOKORO = {"palabrita": "ef_dora", "tic": "em_alex"}
    ESPEAK = {"palabrita": ["-p", "62", "-s", "120"], "tic": ["-p", "85", "-s", "135"]}

    def __init__(self, motor, cache, velocidad=0.85):
        self.cache, self.vel, self.kokoro = cache, velocidad, None
        if motor in ("auto", "kokoro"):
            try:
                from kokoro import KPipeline
                self.kokoro = KPipeline(lang_code="e")
            except Exception as e:
                if motor == "kokoro":
                    sys.exit(f"Kokoro no disponible: {e}")
                print(f"[aviso] Kokoro no disponible ({type(e).__name__}); uso espeak-ng")
        self.motor = "kokoro" if self.kokoro else "espeak"

    def decir(self, texto, personaje="palabrita"):
        personaje = personaje if personaje in self.ESPEAK else "palabrita"
        out = os.path.join(self.cache, f"voz_{self.motor}_{h(texto, personaje, self.vel)}.wav")
        if os.path.exists(out):
            return out
        bruto = out + ".raw.wav"
        if self.kokoro:
            import numpy as np, soundfile as sf
            trozos = [a for _, _, a in self.kokoro(texto, voice=self.VOCES_KOKORO[personaje], speed=self.vel)]
            sf.write(bruto, np.concatenate(trozos), 24000)
        else:
            run(["espeak-ng", "-v", "es", *self.ESPEAK[personaje], "-w", bruto, texto])
        # Tic: voz más aguda (pájaro)
        filtro = "asetrate=24000*1.18,aresample=24000,atempo=0.9" if personaje == "tic" and self.kokoro else None
        a_formato(bruto, out, filtro)
        os.remove(bruto)
        return out


# ---------------- música ----------------
NOTAS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def nota_midi(n):
    m = re.fullmatch(r"([A-G])(#|b)?(\d)", n)
    v = NOTAS[m[1]] + (1 if m[2] == "#" else -1 if m[2] == "b" else 0)
    return 12 * (int(m[3]) + 1) + v


def frases(cancion):
    """Lista de frases; cada frase es una lista de (nota, duración en unidades)."""
    return [[(t.split(":")[0], float(t.split(":")[1])) for t in f.split()]
            for f in cancion["notas"].split("|")]


def render_cancion(cancion, tempo, cache, repeticiones=1):
    """Devuelve (wav, duraciones de cada frase en segundos) para UNA pasada."""
    fr = frases(cancion)
    seg_unidad = 60 / tempo
    out = os.path.join(cache, f"musica_{h(cancion['notas'], tempo, repeticiones)}.wav")
    durs = [sum(d for _, d in f) * seg_unidad for f in fr]
    if not os.path.exists(out):
        tpb = 480
        mid = mido.MidiFile(ticks_per_beat=tpb)
        mel, baj = mido.MidiTrack(), mido.MidiTrack()
        mid.tracks += [mel, baj]
        mel.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo)))
        mel.append(mido.Message("program_change", program=12, channel=0))   # marimba
        baj.append(mido.Message("program_change", program=32, channel=1))   # bajo acústico
        for _ in range(repeticiones):
            for f in fr:
                for n, d in f:
                    t = int(d * tpb)
                    mel.append(mido.Message("note_on", note=nota_midi(n), velocity=96, channel=0, time=0))
                    mel.append(mido.Message("note_off", note=nota_midi(n), velocity=0, channel=0, time=t))
                # bajo: tónica de la primera nota de la frase, dos octavas abajo, toda la frase
                raiz = nota_midi(f[0][0]) - 24
                t = int(sum(d for _, d in f) * tpb)
                baj.append(mido.Message("note_on", note=raiz, velocity=70, channel=1, time=0))
                baj.append(mido.Message("note_off", note=raiz, velocity=0, channel=1, time=t))
        midi = out + ".mid"
        mid.save(midi)
        bruto = out + ".raw.wav"
        run(["fluidsynth", "-ni", "-g", "0.8", "-r", "44100", "-F", bruto, SF2, midi])
        total = sum(durs) * repeticiones + 0.6
        a_formato(bruto, out, f"atrim=0:{total:.3f},afade=t=out:st={total-0.6:.3f}:d=0.6")
        os.remove(bruto); os.remove(midi)
    return out, durs


# ---------------- imagen ----------------
class Lienzo:
    def __init__(self, cache):
        self.cache = cache

    def png(self, svg_txt, ancho):
        out = os.path.join(self.cache, f"img_{h(svg_txt, ancho)}.png")
        if not os.path.exists(out):
            src = out[:-4] + ".svg"
            open(src, "w", encoding="utf-8").write(svg_txt)
            run(["rsvg-convert", "-w", str(ancho), src, "-o", out])
            os.remove(src)
        return out

    def sprite(self, nombre, ancho=420, sombra=False):
        f = D.ANIMALES.get(nombre) or D.PERSONAJES.get(nombre)
        s = f()
        return self.png(D.silueta(s) if sombra else s, ancho)


def capa(png, x, y, anim="flota", fase=0.0):
    return dict(png=png, x=x, y=y, anim=anim, fase=fase)


def fila(L, nombres, y=330, ancho=420, ocultos=(), interrogantes=()):
    """Coloca varios animales centrados en una fila."""
    n = len(nombres)
    paso = min(ancho + 40, (D.W - 200) // max(n, 1))
    ancho = min(ancho, paso - 20)
    x0 = (D.W - paso * n) // 2 + (paso - ancho) // 2
    capas = []
    for i, a in enumerate(nombres):
        if a in interrogantes:
            capas.append(capa(L.png(D.interrogacion(), ancho), x0 + i * paso, y, "late", i * 0.7))
        elif a not in ocultos:
            capas.append(capa(L.sprite(a, ancho), x0 + i * paso, y + (420 - ancho) // 2, "salta", i * 0.7))
    return capas


def texto_capa(L, t, y=800, tam=150):
    return capa(L.png(D.texto(t, tam), D.W), 0, y, "fijo") if t else None


# ---------------- planos ----------------
class Productor:
    def __init__(self, guion, voz, cache):
        self.g, self.voz, self.cache = guion, voz, cache
        self.L = Lienzo(cache)
        self.planos = []
        self.inicios = {}   # id de escena -> índice del primer plano (para capítulos)

    def plano(self, fondo, capas, audio, sub=None):
        dur = round(duracion(audio) * FPS) / FPS
        self.planos.append(dict(fondo=fondo, capas=[c for c in capas if c], audio=audio, dur=dur, sub=sub))

    def voz_y_pausa(self, texto, personaje, pausa):
        v = self.voz.decir(texto, personaje)
        p = silencio(pausa, os.path.join(self.cache, f"sil_{pausa}.wav"))
        return unir_wav([v, p], os.path.join(self.cache, f"vp_{h(v, pausa)}.wav"))

    def personaje_capa(self, nombre, x=60):
        return capa(self.L.sprite(nombre, 380), x, 560, "flota") if nombre else None

    # --- tipos de escena ---
    def escena(self, e):
        self.inicios[e["id"]] = len(self.planos)
        t = e["tipo"]
        fondo = e.get("fondo", "liso")
        per = e.get("personaje")
        lineas = e["voz"] if isinstance(e.get("voz"), list) else ([e["voz"]] if e.get("voz") else [])
        pausa = e.get("pausa", 1)

        if t == "cancion":
            return self.cancion(e)

        for i, linea in enumerate(lineas):
            capas = [self.personaje_capa(per)]
            pantalla = e.get("pantalla")
            if t == "gancho":
                capas += fila(self.L, e["animales_preview"], y=380, ancho=210)
            elif t in ("narracion", "repeticion") and e.get("animal"):
                capas.append(capa(self.L.sprite(e["animal"], 560), 680, 180, "salta"))
                if e.get("colores"):
                    capas.append(capa(self.L.png(D.muestra_color(e["colores"]), 360), 1380, 250, "late"))
            elif t == "contar":
                capas += fila(self.L, [e["animal"]] * e["cantidad"], y=300, ancho=380)
            elif t == "quien_falta":
                todos = e["animales"]
                if i == 0:
                    capas += fila(self.L, todos)
                elif i == 1:
                    capas += fila(self.L, todos, interrogantes=[e["falta"]])
                else:
                    capas += fila(self.L, todos)
                pantalla = None if i < 2 else lineas[i].strip("¡!")
            elif t == "repaso":
                a = e["animales"][i % len(e["animales"])]
                capas.append(capa(self.L.sprite(a, 560), 680, 180, "salta"))
                pantalla = None
            if t == "repeticion":
                pantalla = e.get("pantalla") if i == 0 else lineas[i].split("!")[-1].strip(" .").upper() or e.get("pantalla")
            capas.append(texto_capa(self.L, pantalla))
            audio = self.voz_y_pausa(linea, per or "palabrita", pausa)
            self.plano(fondo, capas, audio, sub=linea)

    def cancion(self, e):
        c = self.g["canciones"][e["cancion"]]
        tempo = e.get("tempo", c["tempo"])
        rep = e.get("repeticiones", 1)
        wav, durs = render_cancion(c, tempo, self.cache, rep)
        lineas = [l.format(**e.get("letra_vars", {})) for l in c["letra"]]
        por_linea = len(durs) // len(lineas)
        tiempos = [sum(durs[i * por_linea:(i + 1) * por_linea]) for i in range(len(lineas))]
        # trocear el WAV de la canción en planos por línea de letra
        with wave.open(wav) as w:
            datos = w.readframes(w.getnframes())
        pos = 0
        protas = [e["animal"]] if e.get("animal") else ["palabrita", "tic"]
        for r in range(rep):
            for i, (linea, d) in enumerate(zip(lineas, tiempos)):
                ultimo = r == rep - 1 and i == len(lineas) - 1
                n = len(datos) - pos if ultimo else int(round(d * FPS) / FPS * AR) * 2
                trozo = os.path.join(self.cache, f"can_{h(wav, r, i)}.wav")
                with wave.open(trozo, "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(AR)
                    w.writeframes(datos[pos:pos + n])
                pos += n
                capas = fila(self.L, protas, y=260, ancho=480)
                if e.get("instrumental"):
                    self.plano(e.get("fondo", "liso"), capas, trozo)
                    continue
                if r > 0:
                    capas.append(capa(self.L.png(D.texto("¡Ahora tú!", 90, "#ffe066", D.W, 160), D.W), 0, 40, "late"))
                capas.append(texto_capa(self.L, linea, y=800, tam=110))
                self.plano(e.get("fondo", "liso"), capas, trozo, sub="♪ " + linea)

    # --- render ---
    def render_plano(self, p, salida, ancho):
        ins, filtros = ["-loop", "1", "-t", f"{p['dur']:.2f}", "-i", self.L.png(D.fondo(p["fondo"]), D.W)], []
        ultimo = "0:v"
        for k, c in enumerate(p["capas"], 1):
            ins += ["-loop", "1", "-t", f"{p['dur']:.2f}", "-i", c["png"]]
            f = c["fase"]
            y = {"flota": f"{c['y']}+12*sin(2*PI*0.5*t+{f})",
                 "salta": f"{c['y']}-abs(28*sin(2*PI*0.7*t+{f}))",
                 "late": f"{c['y']}+6*sin(2*PI*1.2*t+{f})",
                 "fijo": str(c["y"])}[c["anim"]]
            filtros.append(f"[{ultimo}][{k}:v]overlay=x={c['x']}:y='{y}':eval=frame[v{k}]")
            ultimo = f"v{k}"
        fade = max(0.0, p["dur"] - 0.2)
        filtros.append(f"[{ultimo}]scale={ancho}:-2,format=yuv420p,fade=t=in:d=0.2,fade=t=out:st={fade:.2f}:d=0.2[out]")
        run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filtros),
             "-map", "[out]", "-r", str(FPS), "-t", f"{p['dur']:.2f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", salida])

    def render(self, salida, ancho):
        tmp = os.path.join(self.cache, "planos"); os.makedirs(tmp, exist_ok=True)
        lista, audios = [], []
        for i, p in enumerate(self.planos):
            f = os.path.join(tmp, f"p{i:04d}_{h(p['fondo'], p['capas'], p['dur'], ancho)}.mp4")
            if not os.path.exists(f):
                self.render_plano(p, f, ancho)
            lista.append(f)
            audios.append(unir_wav([p["audio"]], os.path.join(tmp, f"a{i:04d}.wav"), total=p["dur"]))
            print(f"\r  plano {i+1}/{len(self.planos)}", end="", flush=True)
        print()
        txt = os.path.join(tmp, "lista.txt")
        open(txt, "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in lista))
        audio = unir_wav(audios, os.path.join(tmp, "audio.wav"))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", txt, "-i", audio,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", salida])
        self.srt(salida[:-4] + ".srt")
        self.tiempos(salida[:-4] + ".tiempos.json")

    def tiempos(self, ruta):
        acumulado, t = [], 0.0
        for p in self.planos:
            acumulado.append(t); t += p["dur"]
        json.dump({"duracion": t, "escenas": {k: round(acumulado[i], 2) for k, i in self.inicios.items() if i < len(acumulado)}},
                  open(ruta, "w", encoding="utf-8"), indent=1)

    def srt(self, ruta):
        def ts(s):
            return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d},{int(s*1000%1000):03d}"
        t, n, out = 0.0, 0, []
        for p in self.planos:
            if p["sub"]:
                n += 1
                out.append(f"{n}\n{ts(t)} --> {ts(t + p['dur'])}\n{p['sub']}\n")
            t += p["dur"]
        open(ruta, "w", encoding="utf-8").write("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--voz", choices=["auto", "kokoro", "espeak"], default="auto")
    ap.add_argument("--ancho", type=int, default=1920)
    ap.add_argument("--limite", type=int, help="Producir solo las N primeras escenas (pruebas)")
    ap.add_argument("--salida", default="salida/videos")
    ap.add_argument("--cache", default="salida/cache")
    a = ap.parse_args()

    for prog in ("ffmpeg", "rsvg-convert", "fluidsynth"):
        if not shutil.which(prog):
            sys.exit(f"Falta '{prog}' en el PATH")
    os.makedirs(a.salida, exist_ok=True); os.makedirs(a.cache, exist_ok=True)
    g = yaml.safe_load(open(a.guion, encoding="utf-8"))
    v = g["video"]
    voz = Voz(a.voz, a.cache, v.get("voz", {}).get("velocidad", 0.85))
    P = Productor(g, voz, a.cache)
    escenas = g["escenas"][:a.limite] if a.limite else g["escenas"]
    for i, e in enumerate(escenas, 1):
        print(f"\r  escena {i}/{len(escenas)}: {e['id']:<20}", end="", flush=True)
        P.escena(e)
    print()
    total = sum(p["dur"] for p in P.planos)
    print(f"  {len(P.planos)} planos, {total/60:.1f} min, voz: {voz.motor}")
    salida = os.path.join(a.salida, f"{v['id']}{'_prueba' if a.limite else ''}.mp4")
    P.render(salida, a.ancho)
    print(f"-> {salida}\n-> {salida[:-4]}.srt\n-> {salida[:-4]}.tiempos.json")


if __name__ == "__main__":
    main()
