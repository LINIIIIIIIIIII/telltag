"""Ingredient / material labeled cross-section, illustration only."""
from __future__ import annotations
from html import escape

def svg_stack(layers: list[tuple[str,str,str]], dye_colour: str) -> str:
    palette={'Package barrier':'#bdcad8','Membrane':'#72a28e','Indicator':'#bb9bb8','Viewing':'#e8e0c6','Mounting':'#d2bca1'}
    parts=[]
    for i,(role,name,detail) in enumerate(layers):
        y=55+i*62
        col=palette.get(role,'#dce7dd')
        if role=='Indicator': col=dye_colour
        parts.append(f'<rect x="25" y="{y}" width="260" height="45" rx="8" fill="{col}" stroke="#739181" stroke-width="1"/>'
                     f'<text x="38" y="{y+17}" fill="#163d2c" font-size="13" font-weight="700">{escape(role)}</text>'
                     f'<text x="38" y="{y+34}" fill="#183b30" font-size="12">{escape(name[:31])}</text>'
                     f'<text x="307" y="{y+28}" fill="#31564a" font-size="13">{escape(detail[:68])}</text>')
    height=72+len(layers)*62
    return f'''<!doctype html><html><head><style>body{{margin:0;background:transparent;font-family:Arial,sans-serif}}svg{{width:100%;height:auto}}</style></head><body><svg viewBox="0 0 850 {height}" role="img" aria-label="Schematic labeled TellTag layer stack"><rect width="850" height="{height}" rx="14" fill="#f5f7f3"/><text x="25" y="30" fill="#214736" font-weight="700" font-size="15">MATERIAL STACK — NOT TO SCALE</text>{''.join(parts)}</svg></body></html>'''
