"""Live illustration of a sticker on a food tray; NOT a photographic food assessment."""
from html import escape
import numpy as np


def _blend(a:str,b:str,frac:float)->str:
    f=float(np.clip(frac,0,1)); aa=[int(a[i:i+2],16) for i in (1,3,5)];bb=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(x*(1-f)+y*f):02x}' for x,y in zip(aa,bb))


def live_beef_svg(sticker_hex:str, hour:float, food_index:float, log_cfu:float,
                  tvbn:float, gas_ppm:float, placement:str, indicator_name:str,
                  has_optical_prediction:bool=True)->str:
    """Shows measured *reference* microbiology labels and a purely illustrative beef surface.
    Does NOT show pathological spoilage, food safety, or a measured product colour.
    """
    f=float(np.clip(food_index,0,1))
    meat_color=_blend('#AE4754','#796054',f)
    meat_shadow=_blend('#812A35','#5B5147',f)
    sticker=sticker_hex if has_optical_prediction else '#D9DDD6'
    plate_note='Hypothetical dye colour' if has_optical_prediction else 'Colour prediction unavailable'
    # The visually changing meat colour is NOT an observed film/food measurement.
    return f'''<!doctype html><html><head><meta charset="utf-8"/><style>
    body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:transparent}}
    svg{{width:100%;height:auto;display:block}}
    </style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1060 440" role="img" aria-label="Illustrative beef aging and TellTag response">
    <defs><linearGradient id="tray" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#ECF0E9"/><stop offset="1" stop-color="#A9B8AE"/></linearGradient>
    <linearGradient id="beef" x1="0" x2="1" y1="0" y2="1"><stop stop-color="{meat_color}"/><stop offset="1" stop-color="{meat_shadow}"/></linearGradient>
    <filter id="shadow"><feDropShadow dx="1" dy="6" stdDeviation="8" flood-opacity=".12"/></filter></defs>
    <rect width="1060" height="440" rx="20" fill="#F5F7F2"/>
    <text x="38" y="45" fill="#214B3A" font-size="19" font-weight="700">BEEF + TELLTAG / LIVE TIMELINE</text>
    <text x="38" y="68" fill="#64796B" font-size="13">Reference beef values from a 4°C study; meat appearance is illustrative</text>
    <g filter="url(#shadow)"><rect x="50" y="135" width="515" height="238" rx="34" fill="url(#tray)" stroke="#99AD9E" stroke-width="4"/>
    <rect x="63" y="149" width="489" height="207" rx="26" fill="#2A3836" opacity=".25"/></g>
    <path d="M155 175 C236 129 359 164 438 214 C512 278 433 350 315 334 C217 353 121 307 132 239 Z" fill="url(#beef)" stroke="#753F3F" stroke-width="4"/>
    <path d="M165 231 C242 209 257 264 320 239 S416 213 429 251 M184 298 C255 267 303 326 405 284" fill="none" stroke="#F1B2A8" opacity="{max(.12,.62-.36*f):.3f}" stroke-width="10" stroke-linecap="round"/>
    <path d="M45 155 L565 155 L579 177 L35 177Z" fill="#EAF5F0" opacity=".45" stroke="#B7C7BE" stroke-width="4"/>
    <g filter="url(#shadow)">
    <rect x="354" y="100" width="183" height="77" rx="13" fill="#F9FBF9" stroke="#CFD9D0" stroke-width="3"/>
    <rect x="366" y="110" width="159" height="54" rx="10" fill="{sticker}" stroke="#667C70" stroke-width="2"/>
    <text x="445" y="143" fill="#FFFFFF" text-anchor="middle" font-size="18" font-weight="700">TELLTAG</text>
    </g>
    <rect x="614" y="101" width="408" height="263" rx="17" fill="#FFFFFF" stroke="#DCE5DD" stroke-width="2"/>
    <text x="640" y="136" fill="#63796B" font-size="14">SIMULATION PLAYHEAD</text>
    <text x="640" y="185" fill="#244B3B" font-size="40" font-weight="700">Day {hour/24:.1f}</text>
    <line x1="640" y1="204" x2="994" y2="204" stroke="#E6EAE5" stroke-width="2"/>
    <text x="640" y="233" font-size="14" fill="#69796E">Study bacterial count</text>
    <text x="989" y="233" text-anchor="end" font-size="21" font-weight="700" fill="#244B3B">{log_cfu:.2f} log CFU/g</text>
    <text x="640" y="267" font-size="14" fill="#69796E">Study TVB-N</text>
    <text x="989" y="267" text-anchor="end" font-size="21" font-weight="700" fill="#244B3B">{tvbn:.1f} mg/100g</text>
    <text x="640" y="303" font-size="14" fill="#69796E">Assumed headspace gas</text>
    <text x="989" y="303" text-anchor="end" font-size="21" font-weight="700" fill="#244B3B">{gas_ppm:.2f} ppm</text>
    <text x="640" y="338" font-size="12" fill="#687E72">{escape(plate_note)}</text>
    <text x="51" y="410" font-size="14" fill="#577364">{escape(placement)} · {escape(indicator_name)}</text>
    <text x="613" y="405" font-size="12" fill="#7D8C83">No food-safety determination</text>
    </svg></body></html>'''


def timelapse_player(frame, base_color:str, acid_color:str, on_color:str|None,
                     title='BE​​EF STORAGE TIMELINE') -> str:
    """Self-running read-only browser replay of computed trajectory, including play/pause.
    No model decisions are made in JS; all values are supplied by the Python simulation.
    """
    import json
    sampled=frame.iloc[::max(1,len(frame)//160)].copy()
    if sampled.index[-1] != frame.index[-1]:sampled=__import__('pandas').concat([sampled,frame.iloc[[-1]]])
    records=[]
    for r in sampled.itertuples(index=False):
        records.append([round(float(r[0]),3),round(float(r[1]),3),round(float(r[2]),3),round(float(r[3]),3),
                        None if __import__('pandas').isna(r[4]) else round(float(r[4]),4)])
    payload=json.dumps(records)
    valid=on_color is not None
    a=acid_color if valid else '#d9ddd6';b=on_color if valid else '#d9ddd6'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;color:#1e3d2e;background:#f7f9f4}}
    .wrap{{border:1px solid #dce9dd;border-radius:20px;padding:22px;background:#f7f9f4}}
    h3{{margin:0 0 6px;font-size:17px}}small{{color:#62766a}}
    .scene{{display:grid;grid-template-columns:1.3fr 1fr;gap:18px;align-items:center;margin-top:20px}}
    .tray{{height:240px;border-radius:28px;background:linear-gradient(#b9c9bd,#81968b);border:9px solid #dce5dd;box-shadow:0 7px 18px #213b3022;position:relative;display:flex;align-items:center;justify-content:center}}
    .meat{{width:70%;height:62%;border-radius:51% 40% 46% 52%;background:#ac4354;border:5px solid #8a3d47;transform:rotate(-8deg);box-shadow:inset 0 -14px 18px #422e3540;transition:background .1s linear}}
    .marble{{position:absolute;left:25%;width:48%;top:50%;height:18px;border-top:9px solid #efb7aa;opacity:.7;transform:rotate(-14deg);border-radius:70%}}
    .sticker{{position:absolute;right:15px;top:12px;background:#fff;border-radius:12px;padding:8px;box-shadow:0 2px 8px #112b2c30}}
    .chip{{background:#e8c54e;padding:10px 20px;border-radius:8px;color:white;font-weight:750;letter-spacing:1px;min-width:115px;text-align:center}}
    .readout{{background:#fff;padding:18px;border-radius:14px;border:1px solid #dfebe2}}
    .day{{font-size:40px;font-weight:750;margin-bottom:14px}}.metric{{display:flex;justify-content:space-between;margin:12px 0;border-bottom:1px solid #edf2eb;padding-bottom:8px;font-size:14px;gap:10px}}
    .ctrl{{display:flex;gap:14px;align-items:center;margin:18px 0 4px}}button{{border:0;background:#205f44;color:white;border-radius:8px;padding:10px 18px;font-weight:700;cursor:pointer}}
    input[type=range]{{flex:1;accent-color:#2c6c51;cursor:pointer}}.warn{{font-size:12px;color:#65786b;margin-top:9px}}
    @media(max-width:600px){{.scene{{grid-template-columns:1fr}}.tray{{height:180px}}.day{{font-size:26px}}}}
    </style></head><body><div class="wrap"><h3>WATCH THE BEEF STUDY + STICKER MODEL</h3><small>Food measurements are interpolated from one 4°C study. Gas and sticker response are assumptions, not observed.</small>
    <div class="scene"><div class="tray"><div id="meat" class="meat"></div><div class="marble"></div><div class="sticker"><div id="chip" class="chip">TELLTAG</div></div></div>
    <div class="readout"><div class="day" id="day">Day 0.0</div>
    <div class="metric"><span>Reference bacteria</span><strong id="bacteria">—</strong></div>
    <div class="metric"><span>Reference TVB-N</span><strong id="tvbn">—</strong></div>
    <div class="metric"><span>Assumed headspace gas</span><strong id="gas">—</strong></div>
    <div class="metric"><span>Modeled dye (not measured)</span><strong id="dye">—</strong></div>
    </div></div><div class="ctrl"><button id="play">▶ Play</button><input type="range" id="time" min="0" max="{len(records)-1}" value="0" step="1" aria-label="Time lapse day"/></div>
    <div class="warn">The steak image is an illustration, not a scientifically predicted appearance. The sticker colour is illustrative. Do not use for food-safety decisions.</div></div>
    <script>
    const data={payload};let i=0;let timer=null;let slider=document.querySelector('#time');
    let acid={json.dumps(a)};let base={json.dumps(b)};const valid={str(valid).lower()};
    function blend(c1,c2,f){{let z='#';f=Math.max(0,Math.min(1,f));for(let k=1;k<=5;k+=2){{let x=parseInt(c1.slice(k,k+2),16),y=parseInt(c2.slice(k,k+2),16);z+=Math.round(x*(1-f)+y*f).toString(16).padStart(2,'0')}}return z}}
    function show(k){{i=k;slider.value=i;const r=data[i];document.querySelector('#day').textContent='Day '+(r[0]/24).toFixed(1);
      document.querySelector('#bacteria').textContent=r[1].toFixed(2)+' log CFU/g';document.querySelector('#tvbn').textContent=r[2].toFixed(1)+' mg/100g';
      document.querySelector('#gas').textContent=r[3].toFixed(2)+' ppm';document.querySelector('#dye').textContent=r[4]===null?'Not modeled':r[4].toFixed(1)+'%';
      const visual=Math.max(0,Math.min(1,(r[1]-3)/(8.64-3)));document.querySelector('#meat').style.background=blend('#ae4754','#796054',visual);
      document.querySelector('#chip').style.background=r[4]===null?'#d9ddd6':blend(acid,base,r[4]/100);
    }}
    function stop(){{if(timer!==null)clearInterval(timer);timer=null;document.querySelector('#play').textContent='▶ Play'}}
    document.querySelector('#play').addEventListener('click',()=>{{if(timer!==null){{stop();return}}
      if(i===data.length-1)show(0);document.querySelector('#play').textContent='❚❚ Pause';
      timer=setInterval(()=>{{if(i>=data.length-1){{stop();return}}show(i+1)}},85);
    }});
    slider.addEventListener('input',e=>{{stop();show(Number(e.target.value))}});show(0);
    </script></body></html>'''
