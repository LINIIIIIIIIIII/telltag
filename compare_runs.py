"""Transparent, descriptive differences between two UNVALIDATED simulation runs.
No chemical causality or statistical significance is inferred automatically.
"""
from __future__ import annotations
from dataclasses import asdict
import math
import pandas as pd
from model import Formulation, crossing_time_hours

# Human-readable output names for user-entered fields.
PARAMETERS = {
 'membrane_thickness_um': ('Membrane thickness', 'µm', 'model input'),
 'membrane_permeability_e15': ('Membrane permeability', '×10⁻¹⁵ SI', 'model assumption'),
 'matrix_thickness_um': ('Indicator-layer thickness', 'µm', 'model input'),
 'matrix_permeability_e15': ('Indicator-layer permeability', '×10⁻¹⁵ SI', 'model assumption'),
 'sorption_capacity_umol_m2_pa': ('Effective gas uptake capacity', 'µmol/m²/Pa', 'model assumption'),
 'buffer_capacity_umol_m2_ph': ('Effective buffer response', 'µmol/m²/pH', 'model assumption'),
 'starting_ph': ('Starting apparent pH', '', 'model assumption'),
 'apparent_pka': ('Apparent film pKa', '', 'model assumption'),
 'acid_color': ('Illustrative acid colour', '', 'visual only'),
 'base_color': ('Illustrative base colour', '', 'visual only'),
}
EXPOSURE = {'max_ppm': ('Assumed gas exposure', 'ppm'),
            'duration_h': ('Simulation duration', 'hours'),
            'profile': ('Gas input profile', ''),
            'package_thickness_um': ('Assumed package barrier thickness', 'µm'),
            'package_permeability_e15': ('Assumed package barrier permeability', '×10⁻¹⁵ SI')}

def snapshot(formulation:Formulation, curve:pd.DataFrame, exposure:dict, visual:dict) -> dict:
    """Store a fully reproducible CURRENT session result, including curve for comparison."""
    return {'formulation':asdict(formulation),
            'exposure':{k:v for k,v in exposure.items() if k!='measured_gas_profile'},
            'visual':dict(visual),
            'hours':curve['Hours'].tolist(),
            'basic_fraction_pct':curve['Basic dye fraction (%)'].tolist(),
            'apparent_ph':curve['Apparent pH'].tolist(),
            'gas_profile_uploaded':exposure.get('profile') == 'Uploaded gas profile'}

def _changed(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return not math.isclose(float(a),float(b),abs_tol=1e-9,rel_tol=1e-9)
    return a!=b

def describe_delta(old:dict,new:dict) -> tuple[pd.DataFrame,list[str]]:
    rows=[]
    for key,(label,unit,kind) in PARAMETERS.items():
        a=old['formulation'].get(key);b=new['formulation'].get(key)
        if _changed(a,b):
            rows.append({'Setting':label,'Earlier':a,'Now':b,'Unit':unit,'Impact type':kind})
    for key,(label,unit) in EXPOSURE.items():
        a=old['exposure'].get(key);b=new['exposure'].get(key)
        if _changed(a,b):
            rows.append({'Setting':label,'Earlier':a,'Now':b,'Unit':unit,'Impact type':'scenario / assumed exposure'})
    for key,label in {'food':'Food illustration','placement':'Sticker placement','viewing':'Viewing layer shown','adhesive':'Adhesive shown','membrane_material':'Named membrane grade (no matched permeability)','matrix_material':'Named matrix grade (no matched permeability)','viewing_material':'Named viewing film','adhesive_material':'Named adhesive','indicator':'Indicator identity (response model NOT connected)','virtual_dry_mass_composition_pct':'Virtual mixture (physics not connected)'}.items():
        a=old['visual'].get(key);b=new['visual'].get(key)
        if _changed(a,b):
            rows.append({'Setting':label,'Earlier':a,'Now':b,'Unit':'','Impact type':'visual only' if key!='placement' else 'visual + assumed barrier'})
    changes=pd.DataFrame(rows,columns=['Setting','Earlier','Now','Unit','Impact type'])
    old_curve=pd.DataFrame({'Hours':old['hours'],'Basic dye fraction (%)':old['basic_fraction_pct']})
    new_curve=pd.DataFrame({'Hours':new['hours'],'Basic dye fraction (%)':new['basic_fraction_pct']})
    old_t=crossing_time_hours(old_curve);new_t=crossing_time_hours(new_curve)
    old_end=float(old_curve['Basic dye fraction (%)'].iloc[-1]);new_end=float(new_curve['Basic dye fraction (%)'].iloc[-1])
    lines=[]
    if len(changes)==0:
        lines.append('You have not changed the recorded settings. Both runs use the same inputs.')
    else:
        names=', '.join(changes['Setting'].tolist())
        lines.append(f'You changed {len(changes)} setting(s): {names}.')
    effect=new_end-old_end
    if abs(effect)<0.05:
        lines.append(f'The calculated final basic-form fraction is effectively unchanged ({old_end:.1f}% vs {new_end:.1f}%).')
    else:
        lines.append(f'At their respective simulation end times, the calculated basic-form fraction changed from {old_end:.1f}% to {new_end:.1f}% ({effect:+.1f} percentage points).')
    if old_t is None or new_t is None:
        lines.append(f'The model 50% crossing was {f"{old_t:.1f} h" if old_t is not None else "not reached"} before and {f"{new_t:.1f} h" if new_t is not None else "not reached"} now. You cannot calculate a time difference if a crossing is missing.')
    else:
        d=new_t-old_t
        if abs(d)<.05:
            lines.append(f'Both model runs reached 50% dye fraction at approximately the same time ({new_t:.1f} h).')
        else:
            lines.append(f'The current model reaches 50% dye fraction {abs(d):.1f} h {"later" if d>0 else "earlier"} than your saved run ({old_t:.1f} h → {new_t:.1f} h).')
    kinds=set(changes['Impact type']) if len(changes) else set()
    if kinds and kinds <= {'visual only'}:
        lines.append('Only visual settings changed. The chemical model is unchanged, so any claimed food-quality difference would be unjustified.')
    if len(changes)==1:
        setting=str(changes.iloc[0]['Setting'])
        explanations={
          'Membrane thickness':'In the model, a thicker membrane raises gas-transport resistance. That often delays the calculated response.',
          'Membrane permeability':'In the model, higher membrane permeability lowers gas-transport resistance and often accelerates uptake.',
          'Indicator-layer thickness':'In the model, a thicker indicator layer increases transport resistance; the real film may have other effects not modeled.',
          'Indicator-layer permeability':'In the model, higher matrix permeability reduces transport resistance.',
          'Effective gas uptake capacity':'This parameter affects both the amount taken up and its response timescale, so the direction may be complex.',
          'Effective buffer response':'In the model, greater buffering produces a smaller apparent pH shift for the same gas uptake.',
          'Starting apparent pH':'This shifts the model dye equilibrium before exposure; it does not demonstrate actual film chemistry.',
          'Apparent film pKa':'This shifts the theoretical equilibrium transition, but the true value in TellTag is unknown.',
          'Assumed gas exposure':'A larger assumed exposure changes the driving pressure. This is not a prediction of gas released from food.',
          'Simulation duration':'You changed how long the model runs, not the chemical recipe.',
          'Gas input profile':'You changed the exposure pattern, so any response difference cannot be attributed to the sticker design.',
          'Sticker placement':'Outside-package mode adds an illustrative package barrier with unmeasured permeability; it is not a measured packaging test.',
          'Food illustration':'Beef, fish and chicken are illustrations only. Changing the picture does not change spoilage chemistry.',
          'Viewing layer shown':'Viewing-layer visibility is purely a drawing option and does not change the model calculations.',
          'Adhesive shown':'Adhesive visibility is purely a drawing option and does not change the model calculations.',
          'Named membrane grade (no matched permeability)':'Switching a named polymer does not change its gas transport until matched measured permeability is provided; the model still uses what-if inputs.',
          'Named matrix grade (no matched permeability)':'Changing the named binder does not change actual uptake/buffering in this model. Those properties require measurement.',
          'Indicator identity (response model NOT connected)':'This model does not predict spectra or reaction chemistry for arbitrary dyes. New identity alone does not validate a curve.',
          'Virtual mixture (physics not connected)':'Percentage changes record a virtual composition, but no measured composition-to-response relationship is modeled.'
        }
        if setting in explanations:
            lines.append('Why the model may differ: '+explanations[setting])
    if len(changes)>1:
        lines.append('You changed multiple inputs, so this comparison cannot isolate which one caused any model difference. Change one at a time for an interpretable sensitivity test.')
    if old['gas_profile_uploaded'] or new['gas_profile_uploaded']:
        lines.append('At least one run used uploaded gas data. To reproduce it exactly later, keep the original gas CSV together with the exported snapshot.')
    if new['exposure'].get('duration_h') != old['exposure'].get('duration_h'):
        lines.append('Runs end at different times; endpoint percentages are not a like-for-like time comparison. Compare the curves at the same hour instead.')
    lines.append('These are differences between hypothetical outputs—not proof that a real sticker improves, or that any food is safe.')
    return changes,lines
