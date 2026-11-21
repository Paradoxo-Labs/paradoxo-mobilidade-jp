"""Gera um HTML navegável com o D3 embutido e a geometria existente."""
from pathlib import Path

source = Path(__file__).resolve().parent
root = source.parent
fragment = (root / 'mapa-rede-joao-pessoa-revisada.html').read_text()
d3 = (source / 'd3.js').read_text()
cdn = '<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'
assert fragment.count(cdn) == 1 and '</script' not in d3.lower()
fragment = fragment.replace(cdn, f'<script>{d3}</script>')
frame = """<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rede proposta de João Pessoa</title>
<style>
:root {
  color-scheme: light dark;
  --font-size-base: 1rem;
  --foreground: light-dark(#1d2530, #f0f3f7);
  --background: light-dark(#fcfdff, #171e2a);
  --muted-foreground: light-dark(#4c5969, #b8c3d2);
  --border: light-dark(#d7e0ea, #39475a);
  --blue: light-dark(#2161ac, #7ab6ff);
  --purple: light-dark(#762ba2, #bf8aef);
  --viz-series-1: light-dark(#4299ff, #83c3ff);
}
body { margin: 0; background: var(--background); font-family: system-ui,sans-serif; }
main { max-width: 78rem; margin: 0 auto; padding: 1rem; }
.form-select { font: inherit; max-width: 100%; }
.text-small { font-size: .875rem; }
.text-muted { color: var(--muted-foreground); }
</style>
<body><main>
"""
(root / 'mapa.html').write_text(frame + fragment + '</main></body></html>\n')
print('mapa.html pronto para abrir diretamente no navegador.')
