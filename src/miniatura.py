"""Genera la miniatura 1280x720 (PNG, < 2 MB) con los dibujos del canal.

Uso: python src/miniatura.py guiones/video01_publicacion.yaml salida/videos/video01_miniatura.png
"""
import os, re, subprocess, sys
import yaml
sys.path.insert(0, os.path.dirname(__file__))
import dibujos as D


def interior(svg_txt):
    return svg_txt[svg_txt.index(">") + 1:-len("</svg>")]


def miniatura(cfg, salida):
    fondo = interior(D.fondo("granja"))
    capas = ""
    animales = cfg["animales"]
    for i, a in enumerate(animales):  # animales grandes, ligeramente solapados
        x = 560 + i * 430
        capas += f'<g transform="translate({x} 330) scale(1.45)">{interior(D.ANIMALES[a]())}</g>'
    capas += f'<g transform="translate(40 470) scale(1.3)">{interior(D.palabrita())}</g>'
    t = cfg["texto"]
    capas += (f'<text x="960" y="250" font-family="{D.FUENTE}" font-weight="900" font-size="230" text-anchor="middle" '
              f'fill="#ffe066" stroke="{D.TINTA}" stroke-width="28" paint-order="stroke" stroke-linejoin="round">{t}</text>')
    src = salida[:-4] + ".svg"
    open(src, "w", encoding="utf-8").write(D.svg(fondo + capas, D.W, D.H))
    subprocess.run(["rsvg-convert", "-w", "1280", src, "-o", salida], check=True)
    os.remove(src)
    return salida


if __name__ == "__main__":
    cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["miniatura"]
    os.makedirs(os.path.dirname(sys.argv[2]) or ".", exist_ok=True)
    print("->", miniatura(cfg, sys.argv[2]))
