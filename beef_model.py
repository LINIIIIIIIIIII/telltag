"""Beef quality reference data and an EXPLICITLY HYPOTHETICAL gas link.

Measured food data: refrigerated beef study at 4 C. No headspace-ppm-to-TVBN
mapping or sticker response has been measured for this exact TellTag system.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

DATA=Path(__file__).parent/'data'/'food_spoilage_measurements.csv'
BEEF_URL='https://www.mdpi.com/2304-8158/14/23/4017'
E_NOSE_URL='https://pmc.ncbi.nlm.nih.gov/articles/PMC10252673/'


def measured_beef():
    frame=pd.read_csv(DATA)
    frame=frame[frame['study_id']=='BEEF_2025'].copy()
    return frame


def source_series(measurement:str)->pd.DataFrame:
    d=measured_beef()
    d=d[d.measurement==measurement].sort_values('day').copy()
    if d.empty: raise ValueError('Unknown or unavailable beef measurement: '+str(measurement))
    return d


def benchmark_time_hours(benchmark=7.0)->float|None:
    d=source_series('Total bacterial count')
    x=d.day.to_numpy(dtype=float)*24
    y=d.value.to_numpy(dtype=float)
    if benchmark>y.max() or benchmark<y.min(): return None
    return float(np.interp(benchmark,y,x))


def beef_reference(duration_h:float=240, n:int=481, temp_c:float=4,
                   use_assumed_q10:bool=False, q10:float=2.)->pd.DataFrame:
    """Within-study interpolation only at 4 C. Temp scaling is flagged assumption."""
    if duration_h<=0 or duration_h>240: raise ValueError('Study range only: duration <= 240 hours')
    if n<2: raise ValueError('Need at least two time points')
    if not 1.0<=q10<=5.0: raise ValueError('Q10 scenario input out of bounds')
    if temp_c!=4 and not use_assumed_q10:
        raise ValueError('For other temperatures, turn on hypothetical scaling or use only 4 C reference')
    hours=np.linspace(0,duration_h,n)
    mult=q10**((temp_c-4)/10) if use_assumed_q10 else 1.
    age=np.clip(hours*mult,0,240)
    out={'Hours':hours, 'Study-equivalent age (h)':age}
    for metric,col in [('Total bacterial count','Beef bacteria (log CFU/g)'),('TVB-N','Beef TVB-N (mg N/100g)'),('Meat pH','Beef tissue pH')]:
        sample=source_series(metric)
        out[col]=np.interp(age,sample.day.to_numpy(float)*24,sample.value.to_numpy(float))
    return pd.DataFrame(out)


def scenario_gas_profile(beef:pd.DataFrame, end_ppm:float=7., start_ppm:float=0.,
                         bridge_metric:str='TVB-N', exponent:float=1.0)->pd.DataFrame:
    """Scenario curve: normalize 4 C food trend, then ASSUME ppm scales with it.

    In particular, beef TVB-N mg/100g is NOT converted to headspace ppm. The
    dimensionless normalization and selected ppm range are user assumptions.
    """
    if end_ppm<start_ppm or start_ppm<0 or end_ppm>1e4: raise ValueError('ppm limits invalid')
    if exponent<=0: raise ValueError('Exponent must be positive')
    col={'TVB-N':'Beef TVB-N (mg N/100g)', 'Bacterial count':'Beef bacteria (log CFU/g)'}[bridge_metric]
    anchor=source_series('TVB-N' if bridge_metric=='TVB-N' else 'Total bacterial count')
    low=float(anchor.value.iloc[0]);high=float(anchor.value.iloc[-1]);
    if high<=low: raise ValueError('No increasing anchor data')
    normalized=np.clip((beef[col].to_numpy(float)-low)/(high-low),0,1)
    ppm=start_ppm+(end_ppm-start_ppm)*(normalized**exponent)
    return pd.DataFrame({'hours':beef['Hours'].astype(float), 'headspace_ppm':ppm})


def visual_progress_from_beef(bacteria_log:float)->float:
    """Illustration severity index only, NOT a food appearance measurement."""
    return float(np.clip((bacteria_log-3.0)/(8.64-3.0),0.,1.))


def compare_warning(model_cross_h:float|None, benchmark_h:float|None)->str:
    if model_cross_h is None: return 'The model dye did not reach the chosen midpoint during the selected simulation.'
    if benchmark_h is None: return 'No reference bacterial benchmark is available.'
    diff=benchmark_h-model_cross_h
    return (f'The model dye threshold was {abs(diff):.1f} hours '
            +('BEFORE' if diff>=0 else 'AFTER')
            + ' the interpolated research bacterial benchmark. Both the gas link and film parameters are unvalidated; this is not real detection performance.')
