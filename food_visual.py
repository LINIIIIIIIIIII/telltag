"""Clearly illustrative food and sticker visualization; never a food-safety result."""
from __future__ import annotations
import json
from html import escape
import math

PALETTE={'Beef':('#B5515A','#766057'),'Chicken':('#E4BFA5','#998A7A'),'Salmon':('#EA8A75','#9A7C71')}

def _blend(a,b,f):
    f=max(0.,min(1.,float(f)))
    av=[int(a[i:i+2],16) for i in (1,3,5)];bv=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join('%02x'%round(v*(1-f)+w*f) for v,w in zip(av,bv))

def food_svg(food,sticker_hex,hour,duration,tvbn,bacter,gas,placement,indicator,modeled,has_food):
    base,aged=PALETTE[food];meat=_blend(base,aged,hour/duration)
    interior={'Beef':'''<path d="M91 186 C132 115 349 133 419 190 S430 316 275 308 S92 275 91 186Z" fill="MEAT"/><path d="M128 222 Q215 194 286 243 T391 239 M157 270 Q235 244 327 279" stroke="#F3BCAD" opacity=".45" fill="none" stroke-width="8"/>''',
    'Chicken':'''<path d="M100 208 C114 150 210 137 263 151 S387 145 425 196 Q463 249 392 284 T208 307 Q113 291 100 208Z" fill="MEAT"/><path d="M152 214 Q255 184 385 222" stroke="#F9DED0" stroke-width="10" opacity=".4" fill="none"/>''',
    'Salmon':'''<path d="M99 166 Q284 99 437 191 L376 281 Q239 318 106 253 Z" fill="MEAT"/><path d="M125 181 Q235 158 396 202 M119 205 Q245 180 382 228 M133 228 Q234 215 367 246" stroke="#F6CBB4" stroke-width="9" opacity=".64" fill="none"/>'''}[food].replace('MEAT',meat)
    tvbn_text='—' if not has_food or math.isnan(tvbn) else f'{tvbn:.1f} mg N/100g'
    bacteria_text='not in dataset' if math.isnan(bacter) else f'{bacter:.2f} log CFU/g'
    sticker=sticker_hex if modeled else '#D9DDD7'
    return f'''<html><body style="margin:0;font-family:Arial,sans-serif"><svg viewBox="0 0 920 355" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Illustrative {food} package with TellTag indicator">
<rect width="920" height="355" rx="18" fill="#F6F8F3"/><text x="28" y="33" font-size="18" fill="#254B3A" font-weight="700">{escape(food.upper())} / STUDY PLAYBACK</text>
<text x="28" y="55" font-size="12" fill="#65796C">Food and indicator colours are illustrations, not laboratory photos.</text>
<rect x="30" y="96" width="485" height="211" rx="35" fill="#DCE7DC" stroke="#ABBDB0" stroke-width="4"/><rect x="48" y="110" width="448" height="182" rx="29" fill="#49655E" opacity=".23"/>
{interior}
<rect x="346" y="85" width="145" height="65" rx="12" fill="#FFFFFF" stroke="#A1B3A8" stroke-width="2"/><rect x="357" y="94" width="123" height="45" rx="8" fill="{sticker}"/><text x="418" y="121" text-anchor="middle" fill="white" font-weight="bold" font-size="14">TELLTAG</text>
<rect x="550" y="85" width="340" height="236" rx="17" fill="#FFFFFF" stroke="#E0E8DF" stroke-width="2"/><text x="568" y="117" font-size="14" fill="#59705F">STUDY TIME</text><text x="568" y="164" font-size="37" font-weight="700" fill="#254B3A">Day {hour/24:.1f}</text>
<text x="568" y="202" font-size="13" fill="#596F61">Food TVB-N</text><text x="873" y="202" font-size="14" text-anchor="end" fill="#254B3A">{tvbn_text}</text>
<text x="568" y="232" font-size="13" fill="#596F61">Bacteria</text><text x="873" y="232" font-size="14" text-anchor="end" fill="#254B3A">{bacteria_text}</text>
<text x="568" y="262" font-size="13" fill="#596F61">Assumed gas</text><text x="873" y="262" font-size="14" text-anchor="end" fill="#254B3A">{gas:.2f} ppm</text>
<text x="568" y="296" font-size="12" fill="#A2633E">NOT A FRESHNESS OR SAFETY VERDICT</text>
<text x="31" y="338" font-size="12" fill="#65786B">{escape(indicator)} · {escape(placement)}</text></svg></body></html>'''

def food_player(food,frame,acid_color,base_color):
    sampled=frame.iloc[::max(1,len(frame)//160)]
    if sampled.index[-1]!=frame.index[-1]:
        sampled=__import__('pandas').concat([sampled,frame.iloc[[-1]]])
    records=[]
    for r in sampled.itertuples(index=False):
        arr=[float(r[0]),float(r[1]),float(r[2]),None if __import__('pandas').isna(r[3]) else float(r[3])]
        records.append(arr)
    data=json.dumps(records)
    a,b=PALETTE[food]
    return '''<!doctype html><html><body style="margin:0;background:#F7FAF5;font:14px Arial,sans-serif;color:#284B39"><div style="padding:14px;border:1px solid #DFE7DF;border-radius:14px"><b>STUDY TIMELINE — '''+escape(food.upper())+'''</b> <button id="play" style="margin-left:14px;padding:8px 18px;border:0;border-radius:8px;background:#27563E;color:white;cursor:pointer">Play</button> <button id="reset" style="padding:8px;border-radius:8px">Reset</button><br/><input type="range" id="slider" min="0" value="0" style="width:100%;margin-top:18px"/><div style="height:125px;display:flex;align-items:center;gap:22px"><div id="food" style="height:95px;width:185px;border:12px solid #DFE7DF;border-radius:40% 35% 42% 35%;transition:background .2s"></div><div id="sticker" style="height:82px;width:150px;border:8px solid white;border-radius:13px;box-shadow:0 1px 7px #ccc;display:grid;place-items:center;color:white;font-weight:bold">TELLTAG</div><div id="info" style="line-height:1.6"></div></div><small style="color:#7A817A">Food appearance and sticker colours are illustrative. Gas levels are assumed and are not actual measured headspace values.</small></div><script>
const data='''+data+''';const colorA='''+json.dumps(a)+''';const colorB='''+json.dumps(b)+''';const dyeA='''+json.dumps(acid_color)+''';const dyeB='''+json.dumps(base_color)+''';let i=0,handle=null;const slider=document.getElementById('slider'),play=document.getElementById('play');slider.max=data.length-1;
function blend(a,b,f){const v=(s,i)=>parseInt(s.substr(i,2),16);f=Math.max(0,Math.min(1,f));return '#'+[1,3,5].map(i=>Math.round(v(a,i)*(1-f)+v(b,i)*f).toString(16).padStart(2,'0')).join('')}
function render(){const v=data[i];slider.value=i;document.getElementById('food').style.background=blend(colorA,colorB,i/(data.length-1));document.getElementById('sticker').style.background=dyeB===null?'#D9DDD7':blend(dyeA,dyeB,(v[3]||0)/100);document.getElementById('info').innerHTML='<b>Day '+(v[0]/24).toFixed(1)+'</b><br/>TVB-N: '+v[1].toFixed(1)+' mg N/100g<br/>Assumed gas: '+v[2].toFixed(2)+' ppm'}
function stop(){if(handle!==null){clearInterval(handle);handle=null}play.textContent='Play'}
play.onclick=()=>{if(handle!==null){stop();return}play.textContent='Pause';handle=setInterval(()=>{i=(i+1)%data.length;render()},110)};document.getElementById('reset').onclick=()=>{stop();i=0;render()};slider.oninput=()=>{i=Number(slider.value);render()};render();
</script></body></html>'''
