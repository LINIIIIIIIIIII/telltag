"""Measured study-specific food profiles, never product freshness predictions.
Sources are in data/food_study_provenance.csv and studies below.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

DATA=Path(__file__).parent/'data'/'food_spoilage_measurements.csv'
FOODS={
 'Beef':{'study':'BEEF_2025','name':'Beef loin','days':10,'ref_temp':4,'package':'PP tray + PE film','marker':'TVB-N','source':'https://www.mdpi.com/2304-8158/14/23/4017','measurement_count':6,'bench':'7 log CFU/g bacterial research benchmark, within this study only','quality_time_d':None,'qual_source':'Bacterial count, TVB-N and meat pH were measured on 6 dates.'},
 'Chicken':{'study':'CHICKEN_2026','name':'Chicken breast','days':15,'ref_temp':4,'package':'Vacuum-packed','marker':'TVB-N','source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13298445/','measurement_count':10,'bench':'Sensory panel rejection in this study (day 13); not a universal cutoff','quality_time_d':13.,'qual_source':'TVB-N and meat pH were sampled; this study also reported sensory scores and microbial findings.'},
 'Salmon':{'study':'SALMON_2017','name':'Salmon fillet','days':10,'ref_temp':4,'package':'Study fillet storage conditions','marker':'TVB-N','source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC5756197/','measurement_count':2,'bench':'No independently verified sticker warning time; only TVB-N endpoints shown here','quality_time_d':None,'qual_source':'Only the day-0 and day-10 TVB-N endpoints are available in this local dataset.'},
}
MARKERS={
 'Beef':[('Methylamine, dimethylamine, trimethylamine','Reported headspace markers in the selected study','https://www.mdpi.com/2304-8158/14/23/4017')],
 'Chicken':[('Ammonia / volatile nitrogen','Possible target for basic-dye indicators; chemistry varies by packaging','https://pmc.ncbi.nlm.nih.gov/articles/PMC13298445/'),('Acetoin, short-chain acids, sulfur compounds','Can contribute to spoilage signals outside a generic amine response','https://pmc.ncbi.nlm.nih.gov/articles/PMC12523974/')],
 'Salmon':[('Trimethylamine, ammonia and other volatile amines','Established fish-spoilage targets, not unique to salmon','https://www.tandfonline.com/doi/full/10.1080/87559129.2023.2221332'),('Methylglyoxal, benzyl alcohol, acetic acid','Candidate markers identified specifically in salmon; simple pH dye will not selectively measure these','https://pubmed.ncbi.nlm.nih.gov/41267257/')]
}

# Evidence categories are per FOOD not claims of food-safety validation.
INDICATOR_EVIDENCE={
 'BCP':{'Beef':('Research context','Amine/pH indicator family; no prototype-specific proof','https://pmc.ncbi.nlm.nih.gov/articles/PMC9043016/'),
        'Chicken':('Direct chicken research','BCP pH indicator tested with chicken; separate study formulation','https://pmc.ncbi.nlm.nih.gov/articles/PMC6049484/'),
        'Salmon':('Fish-family research only','BCP-containing films tested for fish freshness; not validated for this exact salmon package','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/')},
 'BTB':{'Beef':('Related research','BTB investigated in meat freshness sensing studies','https://pmc.ncbi.nlm.nih.gov/articles/PMC9043016/'),
        'Chicken':('Related chicken research','BTB appears in multi-indicator chicken sensor research','https://pmc.ncbi.nlm.nih.gov/articles/PMC9043016/'),
        'Salmon':('Fish-family research only','BCP+BTB dual indicator reported for fish; not salmon-specific evidence','https://pubmed.ncbi.nlm.nih.gov/36816881/')},
 'BCG':{'Beef':('Research context','BCG studied in meat headspace indicators','https://pmc.ncbi.nlm.nih.gov/articles/PMC9043016/'),
        'Chicken':('Related chicken research','BCG-containing systems reviewed for chicken','https://doi.org/10.1080/87559129.2021.1961270'),
        'Salmon':('Fish-family research only','BCG film investigated for fish; exact salmon response unknown','https://pmc.ncbi.nlm.nih.gov/articles/PMC9043016/')},
 'BCP_CR':{'Beef':('Not established','The published dual dye was evaluated with fish, not this beef package','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/'),
             'Chicken':('Not established','No matching chicken study for this dual dye combination in our reference library','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/'),
             'Salmon':('Fish-family research only','Measured in fish freshness indicator work; specific salmon packaging not validated','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/')},
 'BCP_MR':{'Beef':('Not established','The cited study targets chicken','https://www.mdpi.com/2304-8158/11/21/3533'),
             'Chicken':('Direct chicken research','BCP and methyl red dual indicator tested with chicken fillets; study-specific coating and storage conditions','https://www.mdpi.com/2304-8158/11/21/3533'),
             'Salmon':('Not established','No directly matched salmon validation','https://www.mdpi.com/2304-8158/11/21/3533')},
 'SALMON_CDT':{'Beef':('Not established','Salmon-specific research; not tested for beef here','https://www.sciencedirect.com/science/article/pii/S0003267025009195'),
              'Chicken':('Not established','Salmon-specific research; not tested for chicken here','https://www.sciencedirect.com/science/article/pii/S0003267025009195'),
              'Salmon':('Direct salmon research','Published colorimetric/fluorescent probe for salmon amines, but this design and food-contact suitability are unknown','https://www.sciencedirect.com/science/article/pii/S0003267025009195')},
 'anthobeta':{'Beef':('Direct beef research','Measured film colour response in a particular study','https://pmc.ncbi.nlm.nih.gov/articles/PMC12124793/'),
        'Chicken':('Not established','This film is not validated for the chicken profile','https://pmc.ncbi.nlm.nih.gov/articles/PMC12124793/'),
        'Salmon':('Fish-family research only','Reported in another fish film experiment; salmon package-specific response missing','https://pmc.ncbi.nlm.nih.gov/articles/PMC12124793/')},
 'cabbage':{'Beef':('Not established','Published results not for this beef package','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/'),
        'Chicken':('Related anthocyanin research','Chicken studies use anthocyanins, not necessarily this extract and layer stack','https://pmc.ncbi.nlm.nih.gov/articles/PMC10994710/'),
        'Salmon':('Fish-family research only','Red-cabbage film responses reported for fish; salmon-specific data missing','https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/')},
}

def indicator_evidence(food:str,indicator_id:str)->tuple[str,str,str]:
    e=INDICATOR_EVIDENCE.get(indicator_id,{}).get(food)
    return e if e else ('Not verified for selected food','No matching study for this indicator with these food and package conditions','')


def measured_points(food:str,measurement:str='TVB-N')->pd.DataFrame:
    if food not in FOODS:raise ValueError('Unknown food')
    frame=pd.read_csv(DATA)
    return frame[(frame.study_id==FOODS[food]['study']) & (frame.measurement==measurement)].sort_values('day').copy()


def food_reference(food:str,n:int=481)->pd.DataFrame:
    """Interpolate between observed points for visualization ONLY; no out-of-study extrapolation."""
    if n<2:raise ValueError('n must be >=2')
    p=FOODS[food]
    hours=np.linspace(0,24*p['days'],n)
    tv=measured_points(food,'TVB-N')
    if len(tv)<2:raise ValueError('Missing TVB-N endpoints')
    out={'Hours':hours,'Food TVB-N (mg N/100g)':np.interp(hours,tv.day.to_numpy(float)*24,tv.value.to_numpy(float))}
    for metric,col in [('Total bacterial count','Food bacteria (log CFU/g)'),('Meat pH','Food tissue pH')]:
        d=measured_points(food,metric)
        out[col]=np.interp(hours,d.day.to_numpy(float)*24,d.value.to_numpy(float)) if len(d)>=2 else np.full(n,np.nan)
    return pd.DataFrame(out)


def assumed_gas_profile(food:str,ref:pd.DataFrame,start_ppm:float,end_ppm:float,shape:float=1.,driver='TVB-N')->pd.DataFrame:
    if end_ppm<start_ppm or start_ppm<0 or end_ppm>10000 or shape<=0:raise ValueError('Invalid assumed gas settings')
    if driver=='Bacterial count' and ref['Food bacteria (log CFU/g)'].notna().any(): column='Food bacteria (log CFU/g)'
    else: column='Food TVB-N (mg N/100g)'
    y=ref[column].to_numpy(float)
    span=y[-1]-y[0]
    fraction=np.clip((y-y[0])/span,0,1) if span>0 else np.zeros(len(y))
    return pd.DataFrame({'hours':ref.Hours.to_numpy(float), 'headspace_ppm':start_ppm+(end_ppm-start_ppm)*fraction**shape})


def quality_benchmark(food:str)->float|None:
    if food=='Beef':
        d=measured_points('Beef','Total bacterial count')
        return float(np.interp(7,d.value.to_numpy(float),d.day.to_numpy(float))*24)
    d=FOODS[food]['quality_time_d']
    return None if d is None else d*24.


def food_index(food:str,ref:pd.DataFrame,hour:float)->float:
    # Illustration of relative progress through the study ONLY. Not photographed/measured appearance.
    return float(np.clip(hour/(FOODS[food]['days']*24),0,1))
