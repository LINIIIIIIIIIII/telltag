"""Pure SVG diagrams for the visual TellTag package / layer builder.
Artwork is illustrative: geometry, food, and optical colours are not measured.
"""
from __future__ import annotations
from html import escape


def _food_svg(food: str) -> str:
    if food == 'Fish':
        return '''<g transform="translate(260 226)">
          <path d="M-150 15 C-97 -65,70 -63,125 7 L167 -28 L167 52 L123 26 C52 82,-108 73,-150 15Z" fill="url(#fish)" stroke="#b4c6b6" stroke-width="3"/>
          <path d="M-106 -1 Q-10 -50 83 3 M-94 34 Q-5 61 92 19" fill="none" stroke="#d9e7dc" stroke-width="4" opacity=".7"/>
          <path d="M-6 -43 L37 -76 L55 -37" fill="#bdcfbf" opacity=".7"/>
          <circle cx="-112" cy="12" r="7" fill="#406252"/><circle cx="-114" cy="10" r="2" fill="#fff"/>
          </g>'''
    if food == 'Chicken':
        return '''<g transform="translate(252 215) rotate(-4)">
          <path d="M-143 33 Q-185 -19 -119 -57 Q-63 -89 -9 -50 Q28 -16 80 -30 Q141 -44 147 25 Q135 78 76 84 Q15 85 -33 66 Q-106 89 -143 33Z" fill="url(#chicken)" stroke="#cc9b8d" stroke-width="3"/>
          <path d="M-113 0 Q-60 -35 4 -7 M4 29 Q64 50 107 20" fill="none" stroke="#e9c0b1" stroke-width="8" opacity=".75"/>
          </g>'''
    return '''<g transform="translate(255 216) rotate(-5)">
        <path d="M-153 10 Q-155 -69 -70 -62 Q0 -99 86 -51 Q150 -41 147 21 Q149 83 61 77 Q-25 100 -111 60 Q-148 42 -153 10Z" fill="url(#beef)" stroke="#863c3c" stroke-width="3"/>
        <path d="M-119 -5 C-77 -46 -25 5 9 -30 S102 -44 122 3 M-106 40 C-62 -4 -4 59 34 19 S109 35 124 17" stroke="#f2bbb0" stroke-width="10" fill="none" opacity=".7"/>
        </g>'''


def package_svg(food: str, placement: str, colour: str, hour: float, gas_ppm: float, viewing: bool, adhesive: bool) -> str:
    """2D illustration of package; different food types do not alter the model."""
    food_draw = _food_svg(food)
    sticker_x = 260
    sticker_y = 189 if placement == 'Inside sealed package' else 132
    sticker_display = f'''<g filter="url(#shadow)">
      <rect x="{sticker_x-73}" y="{sticker_y-29}" width="146" height="58" rx="10" fill="#f9faf7" stroke="#d8ddd8" stroke-width="2"/>
      <rect x="{sticker_x-61}" y="{sticker_y-20}" width="122" height="40" rx="8" fill="{colour}" stroke="#708679" stroke-width="1"/>
      <text x="{sticker_x}" y="{sticker_y+5}" font-size="13" text-anchor="middle" fill="#fff" font-weight="700" letter-spacing="1.8">TELLTAG</text>
    </g>'''
    film = '<path d="M78 154 L436 154 L468 183 L52 183Z" fill="#d9e8e3" opacity=".38" stroke="#a1c4b8" stroke-width="3"/>'
    dots = ''.join(f'<circle cx="{95+(i*53)%310}" cy="{155+(i*37)%93}" r="{3+(i%2)}" fill="#368c80" opacity="{.12+.10*(i%4)}"/>' for i in range(14 if gas_ppm > 0 else 0))
    line = '<path d="M448 157 Q527 162 574 146" stroke="#438f79" stroke-width="3" stroke-dasharray="8 8" fill="none" marker-end="url(#arrow)"/>'
    layer_labels = ('VIEWING + ADHESIVE' if viewing and adhesive else 'VIEWING LAYER' if viewing else 'EDGE ADHESIVE' if adhesive else 'MINIMAL STACK')
    return f'''<!doctype html><html><head><style>body{{margin:0;background:transparent;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}}svg{{width:100%;height:auto;display:block}}</style></head><body>
    <svg viewBox="0 0 960 385" role="img" aria-label="Illustration of {escape(food.lower())} in a packaging tray with TellTag sticker">
      <defs><linearGradient id="tray" x2="0" y2="1"><stop stop-color="#d1dacb"/><stop offset="1" stop-color="#aebeb0"/></linearGradient>
      <linearGradient id="fish"><stop stop-color="#b2cac4"/><stop offset=".5" stop-color="#eff0e6"/><stop offset="1" stop-color="#90b5ae"/></linearGradient>
      <linearGradient id="beef"><stop stop-color="#ad575a"/><stop offset=".6" stop-color="#c46b6b"/><stop offset="1" stop-color="#8f3a42"/></linearGradient>
      <linearGradient id="chicken"><stop stop-color="#eec8b2"/><stop offset="1" stop-color="#dba697"/></linearGradient>
      <filter id="shadow"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-opacity=".15"/></filter>
      <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#438f79" stroke-width="1.7"/></marker>
      </defs>
      <rect x="0" y="0" width="960" height="385" rx="20" fill="#f4f5f0"/>
      <text x="42" y="45" fill="#27483a" font-size="16" font-weight="700">PACKAGE PREVIEW</text>
      <text x="42" y="67" fill="#7b897d" font-size="12">Schematic only — food geometry and gas flow are illustrative</text>
      <g filter="url(#shadow)"><path d="M70 174 L440 174 L458 310 L52 310Z" fill="url(#tray)" stroke="#839b8c" stroke-width="4"/><rect x="58" y="153" width="396" height="32" rx="14" fill="#e7eae0" stroke="#aab9ad" stroke-width="3"/></g>
      {food_draw}
      {film}{dots}
      <text x="255" y="343" fill="#395747" font-size="15" font-weight="600" text-anchor="middle">{escape(food)} · sealed tray illustration</text>
      {line}
      <rect x="575" y="153" width="337" height="158" rx="17" fill="#fffdfa" stroke="#d6e2d8"/>
      <text x="603" y="181" font-size="13" fill="#668273">STICKER PLACEMENT</text>
      <text x="603" y="203" font-size="16" font-weight="700" fill="#284e3e">{escape(placement)}</text>
      <text x="603" y="247" font-size="13" fill="#72877b">Illustrative model time</text>
      <text x="603" y="272" font-size="24" font-weight="700" fill="#234f40">{hour:.1f} h</text>
      <text x="745" y="245" font-size="12" fill="#72877b">Gas scenario</text>
      <text x="745" y="268" font-size="20" font-weight="700" fill="#234f40">{gas_ppm:g} ppm</text>
      <text x="575" y="343" font-size="12" fill="#677b70">{layer_labels}</text>
      {sticker_display}
      <text x="480" y="371" font-size="11" fill="#8d9d92">Not to scale · not a food-safety result</text>
    </svg></body></html>'''


def stack_svg(placement: str, membrane_um: float, matrix_um: float, colour: str, viewing: bool, adhesive: bool) -> str:
    """Layer cross-section. Thickness is indicated textually, not to scale."""
    layers = [('Air / package headspace', '#dcefe7','Gas source')]
    if placement == 'Outside sealed package':
        layers.append(('Package film', '#b6d2db', 'Barrier (illustrative property)'))
    layers += [('Selective membrane', '#85aa9c', f'{membrane_um:g} µm · permeability is unverified'),('Indicator matrix', colour, f'{matrix_um:g} µm · effective chemistry is unverified')]
    if viewing:
        layers.append(('Viewing layer', '#e8e7da', 'Visual only · no optical transport modeled'))
    if adhesive:
        layers.append(('Adhesive / edge seal', '#c5b598', 'Visual only · leakage not modeled'))
    rows = []
    for i,(label,fill,desc) in enumerate(layers):
        y=44+i*43
        rows.append(f'<rect x="40" y="{y}" width="260" height="32" rx="7" fill="{fill}" stroke="#99a99d" stroke-width=".7"/><text x="50" y="{y+21}" font-size="13" font-weight="700" fill="#21483b">{escape(label)}</text><text x="328" y="{y+21}" font-size="12" fill="#607e6d">{escape(desc)}</text>')
    total=44+len(layers)*43+16
    return f'''<!doctype html><html><head><style>body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}}svg{{width:100%;height:auto;display:block}}</style></head><body>
    <svg viewBox="0 0 800 {total}" role="img" aria-label="Layer stack visualization">
    <rect width="800" height="{total}" rx="18" fill="#f6f7f3"/>
    <text x="40" y="27" font-size="14" font-weight="700" fill="#254b3d">SENSING PATH · CROSS-SECTION</text>
    {''.join(rows)}
    </svg></body></html>'''
