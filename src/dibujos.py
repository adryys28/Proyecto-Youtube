"""Dibujos originales del canal en SVG (personajes, animales y fondos).

Todo se dibuja por código: estilo 2D plano, colores pastel, contornos suaves.
Cada sprite ocupa un lienzo de 400x400 con el "suelo" en y=380.
"""

W, H = 1920, 1080
TINTA = "#3b2f4a"  # color de contorno
FUENTE = "Nunito, DejaVu Sans, sans-serif"


def svg(contenido, ancho=400, alto=400):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
            f'viewBox="0 0 {ancho} {alto}">{contenido}</svg>')


# ---------- piezas comunes ----------
def ojos(cx, cy, sep=34, r=13, color=TINTA, brillo="#fff"):
    o = ""
    for x in (cx - sep, cx + sep):
        o += (f'<ellipse cx="{x}" cy="{cy}" rx="{r}" ry="{r*1.15}" fill="{color}"/>'
              f'<circle cx="{x+r*0.35}" cy="{cy-r*0.45}" r="{r*0.38}" fill="{brillo}"/>')
    return o


def mejillas(cx, cy, sep=62, color="#ff9db5"):
    return "".join(f'<ellipse cx="{x}" cy="{cy}" rx="17" ry="10" fill="{color}" opacity=".75"/>'
                   for x in (cx - sep, cx + sep))


def sonrisa(cx, cy, ancho=24):
    return (f'<path d="M{cx-ancho} {cy} Q{cx} {cy+ancho*0.9} {cx+ancho} {cy}" '
            f'stroke="{TINTA}" stroke-width="7" fill="none" stroke-linecap="round"/>')


def trazo(color, ancho=6):
    return f'fill="{color}" stroke="{TINTA}" stroke-width="{ancho}" stroke-linejoin="round"'


def patas(xs, y, color, alto=50, ancho=30):
    return "".join(f'<rect x="{x-ancho/2}" y="{y}" width="{ancho}" height="{alto}" rx="13" {trazo(color)}/>'
                   for x in xs)


# ---------- personajes ----------
def palabrita():
    nube = ('M90 300 C40 300 30 230 85 215 C80 150 160 120 200 165 '
            'C230 105 330 120 325 200 C385 205 380 300 320 300 Z')
    return svg(f'<path d="{nube}" {trazo("#ffffff", 8)}/>'
               + ojos(205, 225, 40, 15) + mejillas(205, 262, 75) + sonrisa(205, 262, 22))


def tic():
    return svg(
        f'<path d="M110 250 L40 215 L60 285 Z" {trazo("#5aa9e6")}/>'          # cola
        f'<ellipse cx="200" cy="260" rx="120" ry="105" {trazo("#7cc6fe")}/>'   # cuerpo
        f'<ellipse cx="215" cy="290" rx="65" ry="55" fill="#d6efff"/>'         # barriga
        f'<path d="M280 240 L345 255 L280 275 Z" {trazo("#ffb703")}/>'         # pico
        f'<path d="M160 150 Q175 110 195 150" {trazo("#5aa9e6", 5)}/>'          # plumita
        + ojos(225, 220, 30, 12) + mejillas(225, 250, 55)
        + patas([175, 235], 355, "#ffb703", 28, 14))


# ---------- animales ----------
def _cuerpo(color, rx=140, ry=95, cy=270):
    return f'<ellipse cx="200" cy="{cy}" rx="{rx}" ry="{ry}" {trazo(color)}/>'


def vaca():
    manchas = ('<ellipse cx="140" cy="250" rx="35" ry="25" fill="#2b2b2b"/>'
               '<ellipse cx="260" cy="300" rx="28" ry="20" fill="#2b2b2b"/>')
    return svg(
        patas([110, 160, 240, 290], 320, "#ffffff") + _cuerpo("#ffffff") + manchas
        + f'<path d="M115 110 Q100 70 125 80" {trazo("#f2d398", 5)}/>'
        + f'<path d="M285 110 Q300 70 275 80" {trazo("#f2d398", 5)}/>'
        + f'<ellipse cx="200" cy="165" rx="100" ry="85" {trazo("#ffffff")}/>'
        + f'<ellipse cx="200" cy="210" rx="62" ry="38" {trazo("#ffc2d1")}/>'
        + f'<circle cx="180" cy="210" r="8" fill="{TINTA}"/><circle cx="220" cy="210" r="8" fill="{TINTA}"/>'
        + ojos(200, 150, 38, 12))


def cerdo():
    rosa = "#f7a8c4"
    return svg(
        patas([120, 165, 235, 280], 320, rosa) + _cuerpo(rosa)
        + f'<path d="M335 260 q25 -10 15 15 q-10 15 5 20" stroke="{TINTA}" stroke-width="6" fill="none"/>'
        + f'<path d="M120 105 L150 60 L170 110 Z" {trazo(rosa)}/><path d="M280 105 L250 60 L230 110 Z" {trazo(rosa)}/>'
        + f'<circle cx="200" cy="170" r="92" {trazo(rosa)}/>'
        + f'<ellipse cx="200" cy="200" rx="40" ry="28" {trazo("#ff8fb1")}/>'
        + f'<ellipse cx="186" cy="200" rx="7" ry="10" fill="{TINTA}"/><ellipse cx="214" cy="200" rx="7" ry="10" fill="{TINTA}"/>'
        + ojos(200, 150, 40, 11) + mejillas(200, 200, 68))


def oveja():
    lana = "".join(f'<circle cx="{x}" cy="{y}" r="48" {trazo("#f5f5f5")}/>'
                   for x, y in [(110, 260), (160, 220), (220, 215), (280, 240), (290, 295), (130, 310), (210, 310)])
    return svg(
        patas([130, 170, 230, 270], 320, "#4a4a4a", 50, 24) + lana
        + f'<ellipse cx="200" cy="160" rx="70" ry="80" {trazo("#4a4a4a")}/>'
        + f'<ellipse cx="125" cy="150" rx="35" ry="16" {trazo("#4a4a4a")}/><ellipse cx="275" cy="150" rx="35" ry="16" {trazo("#4a4a4a")}/>'
        + '<circle cx="200" cy="95" r="34" fill="#f5f5f5"/>'
        + ojos(200, 160, 28, 12, "#ffffff", TINTA)
        + sonrisa(200, 195, 16).replace(TINTA, "#ffffff"))


def gallina():
    marron = "#c97b4a"
    return svg(
        patas([170, 230], 335, "#ffb703", 40, 14)
        + f'<path d="M80 230 Q40 170 95 160 Q70 200 110 215 Z" {trazo("#8c4a2f")}/>'
        + f'<ellipse cx="200" cy="260" rx="125" ry="95" {trazo(marron)}/>'
        + f'<path d="M150 250 Q200 300 250 250" {trazo("#b06536", 5)}/>'
        + f'<circle cx="245" cy="150" r="70" {trazo(marron)}/>'
        + f'<path d="M215 90 q10 -35 25 -5 q12 -30 25 0 q15 -20 20 10 Z" {trazo("#e63946", 5)}/>'
        + f'<path d="M305 150 L345 165 L305 180 Z" {trazo("#ffb703", 5)}/>'
        + f'<path d="M300 185 q8 25 -10 25 q-8 -12 0 -25" {trazo("#e63946", 4)}/>'
        + ojos(250, 140, 26, 10))


def pollito():
    amarillo = "#ffd93b"
    return svg(
        patas([170, 230], 345, "#ff8c1a", 32, 12)
        + f'<circle cx="200" cy="250" r="110" {trazo(amarillo)}/>'
        + f'<path d="M115 260 Q80 230 105 210" {trazo(amarillo, 5)}/><path d="M285 260 Q320 230 295 210" {trazo(amarillo, 5)}/>'
        + f'<path d="M200 140 q-8 -25 5 -30 q5 15 0 30" {trazo(amarillo, 4)}/>'
        + f'<path d="M180 245 L220 245 L200 270 Z" {trazo("#ff8c1a", 5)}/>'
        + ojos(200, 215, 36, 12) + mejillas(200, 255, 62))


def caballo():
    marron, crin, hocico = "#a86b3c", "#5b3a1e", "#d9a273"
    return svg(
        patas([120, 165, 235, 280], 315, marron, 60, 28) + _cuerpo(marron, 140, 85, 270)
        + f'<path d="M335 250 q40 25 15 75 q-15 -25 -22 -55" {trazo(crin)}/>'
        + f'<path d="M140 80 L150 20 L185 70 Z" {trazo(marron, 5)}/><path d="M260 80 L250 20 L215 70 Z" {trazo(marron, 5)}/>'
        + f'<ellipse cx="200" cy="150" rx="78" ry="98" {trazo(marron)}/>'
        + f'<path d="M150 70 Q200 30 250 70 Q230 95 200 80 Q170 95 150 70 Z" {trazo(crin, 5)}/>'
        + f'<ellipse cx="200" cy="205" rx="62" ry="45" {trazo(hocico)}/>'
        + f'<ellipse cx="180" cy="200" rx="7" ry="10" fill="{TINTA}"/><ellipse cx="220" cy="200" rx="7" ry="10" fill="{TINTA}"/>'
        + ojos(200, 130, 36, 11) + sonrisa(200, 225, 18))


def pato():
    amarillo = "#ffd93b"
    return svg(
        patas([175, 225], 340, "#ff8c1a", 35, 14)
        + f'<ellipse cx="190" cy="275" rx="135" ry="75" {trazo(amarillo)}/>'
        + f'<path d="M60 250 L30 215 L85 235 Z" {trazo(amarillo)}/>'
        + f'<path d="M150 270 Q200 320 250 265" {trazo("#f4c430", 5)}/>'
        + f'<circle cx="250" cy="160" r="70" {trazo(amarillo)}/>'
        + f'<ellipse cx="325" cy="180" rx="45" ry="18" {trazo("#ff8c1a", 5)}/>'
        + ojos(255, 145, 26, 11) + mejillas(255, 185, 45))


def perro():
    claro, oreja = "#e0b77e", "#8c5a2b"
    return svg(
        patas([120, 165, 235, 280], 320, claro) + _cuerpo(claro)
        + f'<path d="M335 245 q40 -45 35 -70" stroke="{TINTA}" stroke-width="16" fill="none" stroke-linecap="round"/>'
        + f'<path d="M335 245 q40 -45 35 -70" stroke="{claro}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        + f'<circle cx="200" cy="165" r="90" {trazo(claro)}/>'
        + f'<ellipse cx="115" cy="175" rx="30" ry="62" {trazo(oreja)}/><ellipse cx="285" cy="175" rx="30" ry="62" {trazo(oreja)}/>'
        + f'<ellipse cx="200" cy="205" rx="45" ry="32" fill="#f5deb3"/>'
        + f'<ellipse cx="200" cy="190" rx="16" ry="11" fill="{TINTA}"/>'
        + f'<path d="M190 225 q10 25 20 0" {trazo("#ff6b8b", 4)}/>'
        + ojos(200, 150, 36, 12))


ANIMALES = dict(vaca=vaca, cerdo=cerdo, oveja=oveja, gallina=gallina, pollito=pollito,
                caballo=caballo, pato=pato, perro=perro)
PERSONAJES = dict(palabrita=palabrita, tic=tic)


def silueta(svg_txt):
    """Versión en sombra para juegos de adivinar."""
    import re
    s = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', 'fill="#5c5470"', svg_txt)
    return re.sub(r'stroke="#[0-9a-fA-F]{3,6}"', 'stroke="#5c5470"', s)


def interrogacion():
    return svg(f'<circle cx="200" cy="230" r="130" fill="#ffffff" opacity=".85" stroke="{TINTA}" stroke-width="8" '
               f'stroke-dasharray="20 14"/><text x="200" y="300" font-family="{FUENTE}" font-weight="900" '
               f'font-size="200" text-anchor="middle" fill="#7b61ff">?</text>')


# ---------- fondos ----------
def fondo(tipo):
    if tipo == "granja":
        c = ('<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ad9ff"/>'
             '<stop offset="1" stop-color="#d9f2ff"/></linearGradient></defs>'
             f'<rect width="{W}" height="{H}" fill="url(#c)"/>'
             '<circle cx="1700" cy="170" r="95" fill="#ffe066"/>'
             + "".join(f'<g fill="#fff" opacity=".9"><ellipse cx="{x}" cy="{y}" rx="90" ry="38"/>'
                       f'<ellipse cx="{x+60}" cy="{y-25}" rx="60" ry="35"/></g>' for x, y in [(300, 160), (900, 110), (1350, 220)])
             + '<path d="M0 720 Q480 600 960 700 T1920 680 V1080 H0 Z" fill="#8ed081"/>'
             '<path d="M0 820 Q600 760 1200 830 T1920 800 V1080 H0 Z" fill="#6fbf5f"/>'
             '<g transform="translate(1560 560) scale(0.8)"><rect width="300" height="230" fill="#e85d5d" stroke="#3b2f4a" stroke-width="6"/>'
             '<path d="M-30 0 L150 -120 L330 0 Z" fill="#c94444" stroke="#3b2f4a" stroke-width="6"/>'
             '<rect x="110" y="110" width="80" height="120" fill="#fff3e0" stroke="#3b2f4a" stroke-width="6"/></g>'
             + "".join(f'<rect x="{x}" y="760" width="18" height="90" rx="6" fill="#f2d398" stroke="#3b2f4a" stroke-width="4"/>'
                       for x in range(40, 520, 70))
             + '<rect x="30" y="780" width="480" height="14" fill="#f2d398" stroke="#3b2f4a" stroke-width="4"/>')
    elif tipo == "noche":
        c = (f'<rect width="{W}" height="{H}" fill="#2b2d5c"/>'
             '<circle cx="1600" cy="200" r="90" fill="#fff6c9"/><circle cx="1640" cy="175" r="80" fill="#2b2d5c"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff6c9"/>'
                       for x, y, r in [(200, 150, 6), (480, 260, 4), (760, 120, 5), (1100, 230, 6), (1300, 90, 4), (900, 330, 3), (350, 380, 4)])
             + '<path d="M0 800 Q960 700 1920 800 V1080 H0 Z" fill="#3d4a7a"/>')
    else:  # liso
        c = (f'<rect width="{W}" height="{H}" fill="#fff4e6"/>'
             '<circle cx="180" cy="160" r="220" fill="#ffe3ec"/><circle cx="1780" cy="960" r="280" fill="#e3f4ff"/>'
             '<circle cx="1700" cy="140" r="90" fill="#e8ffe3"/>')
    return svg(c, W, H)


def texto(t, tam=150, color="#ffffff", ancho=W, alto=260):
    t = (t or "").replace("&", "&amp;").replace("<", "&lt;")
    return svg(f'<text x="{ancho/2}" y="{alto*0.7}" font-family="{FUENTE}" font-weight="900" font-size="{tam}" '
               f'text-anchor="middle" fill="{color}" stroke="{TINTA}" stroke-width="{tam/9:.0f}" '
               f'paint-order="stroke" stroke-linejoin="round">{t}</text>', ancho, alto)


def muestra_color(colores):
    n = len(colores)
    return svg("".join(f'<circle cx="{200 + (i - (n-1)/2) * 150}" cy="200" r="65" fill="{c}" stroke="{TINTA}" stroke-width="8"/>'
                       for i, c in enumerate(colores)))
