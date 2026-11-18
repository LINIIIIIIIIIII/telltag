"""Evidence-aware material browser for TellTag. No measured amine transport invented."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import pandas as pd

CATALOG = Path(__file__).parent / 'data' / 'materials_catalog.csv'

@lru_cache(maxsize=1)
def load_materials() -> pd.DataFrame:
    df = pd.read_csv(CATALOG, keep_default_na=False)
    if df.id.duplicated().any():
        raise ValueError('Material IDs must be unique')
    return df

def role_ids(role: str) -> list[str]:
    return [r.id for r in load_materials().itertuples(index=False) if role in r.roles.split('|')]

def material(material_id: str) -> dict:
    rows = load_materials().loc[lambda d: d.id == material_id]
    if len(rows) != 1:
        raise ValueError('Unknown material: '+str(material_id))
    return rows.iloc[0].to_dict()

def starting_thickness(material_id: str) -> int:
    return int(float(material(material_id)['example_thickness_um']))

def evidence_label(record: dict) -> str:
    return {
        'SUPPLIER_GAUGES':'Commercially listed supplier gauges (NOT a universal minimum)',
        'PUBLISHED_SINGLE_EXAMPLE':'One measured specimen thickness (NOT a minimum)',
        'PUBLISHED_LAYER_EXAMPLE':'Thickness of a SUBLAYER within a multilayer film',
        'REVIEW_REPORTED_EXAMPLE':'Example measurement summarized in literature (NOT a minimum)',
        'UNVERIFIED_EXAMPLE':'DESIGN PLACEHOLDER only; no measured thickness range in catalog',
    }.get(record['thickness_evidence'],'Insufficient thickness evidence')

def thickness_summary(material_id: str) -> str:
    m=material(material_id)
    a,b=m['documented_low_um'],m['documented_high_um']
    if a != '' and b != '':
        if float(a)==float(b):
            return f"Published single example: {float(a):g} µm. Not a minimum."
        return f"Sourced examples: {float(a):g}–{float(b):g} µm. Not a universal minimum."
    return 'No verified thickness range here; currently showing a hypothetical starter.'

def validate_dry_composition(polymer: float, plasticizer: float, indicator: float) -> tuple[bool,str]:
    numbers = [polymer,plasticizer,indicator]
    if any(n<0 or n>100 for n in numbers):
        return False, 'Each proportion must be from 0% to 100%.'
    total=sum(numbers)
    return (abs(total-100)<1e-7, f'Total: {total:.1f}% dry mass. ' + ('Balanced.' if abs(total-100)<1e-7 else 'Must total exactly 100% for a defined hypothetical composition.'))

def readiness(material_ids: list[str], permeability_verified: bool, film_response_validated: bool = False) -> tuple[str,list[str]]:
    issues=[]
    for mid in material_ids:
        m=material(mid)
        if m['thickness_evidence']=='UNVERIFIED_EXAMPLE':
            issues.append(f"{m['name']}: documented film thickness and exact grade missing")
        if not m['composition_detail'] or 'unknown' in m['composition_detail'].lower():
            issues.append(f"{m['name']}: commercial grade/additives not fully identified")
    if not permeability_verified:
        issues.append('Measured gas-specific permeability is missing for the actual films at the intended temperature and humidity')
    if not film_response_validated:
        issues.append('Prototype-specific sensing kinetics and optical response are not independently validated')
    if issues:
        return 'Research design; NOT a validated digital twin', issues
    return 'Some reference properties recorded; independent full-device validation still required', ['Food threshold and safety evaluation remain necessary']
