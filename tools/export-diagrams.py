#!/usr/bin/env python3
"""Gera PNGs dos diagramas da página de Arquitetura usando o CSS do próprio site.

Extrai cada bloco `<div class="diagram">` de arquitetura.html, monta um harness
que importa styles.css, renderiza com Chrome headless em 2x, corta o fundo
uniforme e reduz para 1600px de largura (2x da largura tipica de README).
Assim o PNG do repositorio e identico ao que aparece no site.

Uso: python3 tools/export-diagrams.py [--site /caminho/do/site]
"""
import argparse
import re
import struct
import subprocess
import sys
from pathlib import Path

SRC_DEFAULT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent.parent / ".diagrams"
SHOT_W = 1240
FINAL_W = 1600

NAMES = {
    "Camadas do sistema": "01-camadas",
    "Arquitetura do runtime edge-ai": "02-componentes-runtime",
    "Fluxo de inferência": "03-fluxo-requisicao",
    "Integração dos apps com o daemon": "04-integracao-apps",
    "Ciclo de vida de um modelo GGUF": "05-ciclo-vida-modelo",
}


def extract_diagrams(html: str):
    """Devolve [(titulo, markup)] de cada .diagram, com contagem de divs balanceada."""
    out = []
    for m in re.finditer(r'<div class="diagram[^"]*">', html):
        start = m.start()
        depth = 0
        for t in re.finditer(r'<div\b[^>]*>|</div>', html[start:]):
            depth += 1 if not t.group(0).startswith("</") else -1
            if depth == 0:
                out.append((start, start + t.end()))
                break
    blocks = []
    for s, e in out:
        block = html[s:e]
        block = block.replace('class="diagram reveal"', 'class="diagram"')
        block = re.sub(r'\s+reveal\b', "", block)
        title = re.search(r'<h3>([^<]+)</h3>', block)
        blocks.append((title.group(1) if title else "diagrama", block))
    return blocks


def harness(markup: str, site: Path) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<link rel="stylesheet" href="file://{site}/styles.css">
<style>
  html,body{{background:#08080a;margin:0}}
  .shot{{width:{SHOT_W}px;padding:36px}}
</style></head>
<body><div class="shot">{markup}</div></body></html>
"""


def png_size(path: Path):
    data = path.read_bytes()[:33]
    return struct.unpack(">II", data[16:24])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=str(SRC_DEFAULT), help="diretorio do site (paginas)")
    args = ap.parse_args()
    site = Path(args.site).resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    html = (site / "arquitetura.html").read_text()
    blocks = extract_diagrams(html)
    if len(blocks) != len(NAMES):
        print(f"esperava {len(NAMES)} diagramas, achei {len(blocks)}", file=sys.stderr)
        return 1

    made = []
    for title, block in blocks:
        if title not in NAMES:
            print(f"titulo desconhecido: {title!r}", file=sys.stderr)
            return 1
        slug = NAMES[title]
        page = OUT / f"{slug}.html"
        png = OUT / f"{slug}.png"
        page.write_text(harness(block, site))
        subprocess.run(
            [
                "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                "--hide-scrollbars", "--force-device-scale-factor=2",
                f"--window-size={SHOT_W},2200", f"--screenshot={png}", str(page),
            ],
            check=True, capture_output=True, timeout=180,
        )
        subprocess.run(
            ["convert", str(png), "-fuzz", "2%", "-trim", "+repage", str(png)],
            check=True, capture_output=True, timeout=180,
        )
        subprocess.run(
            ["convert", str(png), "-resize", f"{FINAL_W}x", "-strip",
             "-define", "png:compression-level=9", str(png)],
            check=True, capture_output=True, timeout=180,
        )
        w, h = png_size(png)
        made.append((slug, w, h, png.stat().st_size))
        print(f"{slug}: {w}x{h} px, {png.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
