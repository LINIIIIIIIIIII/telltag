"""Evidence-backed indicator research records. No chemical exposure/performance extrapolation.

Measured study data refer to SPECIFIC published film and food conditions, NOT TellTag.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / 'data'

@dataclass(frozen=True)
class Indicator:
    id: str
    name: str
    category: str
    studied_on: str
    evidence: str
    finding: str
    main_limit: str
    url: str
    measurement: str
    source_name: str
    sample_colour: str
    research_system: str

INDICATORS = [
    Indicator('cabbage','Red cabbage anthocyanins','Plant-derived pigment','Fish','Measured fish-film colour data',
       'A red-cabbage/PVA indicator film produced measurable colour changes while monitoring fish at 25 C. Colour difference versus starting film was reported at 12 and 24 hours.',
       'Only the exact published film and room-temperature test were measured; no chilled-TellTag response is known.',
       'https://pmc.ncbi.nlm.nih.gov/articles/PMC9653917/','delta_e_cabbage','2022 - Red cabbage puree/PVA fish indicator','#794D8E','Red-cabbage puree + PVA film'),
    Indicator('anthobeta','Anthocyanin + betacyanin blend','Plant-derived pigments','Beef and fish','Measured refrigerated-film colour data',
       'A research film made from mixed anthocyanin and betacyanin pigments was evaluated with beef and fish at 4 C. Published colour-difference measurements are available at days 3, 6, 9 and 12.',
       'These results are for the researchers\' combined film, not individual pigments or TellTag. The colour response is not always monotonic.',
       'https://pmc.ncbi.nlm.nih.gov/articles/PMC12124793/','delta_e_anthobeta','2025 - Anthocyanin/betacyanin indicators for meat','#79567C','Research blend of anthocyanins/betacyanins'),
    Indicator('curcumin','Turmeric / curcumin','Plant-derived pigment','Pork','Published film study; no digitized response curve',
       'A 2026 pork-film study evaluated turmeric in a cassava-flour/PVA matrix at approximately 4 C, reporting visible pH- and spoilage-related colour responses.',
       'Paper abstract reports a film thickness range, but not a calibrated gas-ppm-to-colour curve that could predict TellTag.',
       'https://tis.wu.ac.th/index.php/tis/article/view/11783','none','2026 - Turmeric/cassava flour/PVA pork film','#C58A37','Turmeric pigment in cassava-flour/PVA film'),
    Indicator('blueberry','Blueberry anthocyanins','Plant-derived pigment','Mutton','Published film study; no imported numerical curve',
       'A 2024 study of blueberry anthocyanins in chitosan films reported visible pH sensitivity and a correlation with mutton deterioration measurements.',
       'No source-compatible gas-transport or dye-response constants have been entered for this specific material and package.',
       'https://pmc.ncbi.nlm.nih.gov/articles/PMC10974092/','none','2024 - Chitosan/blueberry anthocyanin mutton film','#744379','Blueberry anthocyanins in chitosan film'),
    Indicator('curcumin_antho','Curcumin + anthocyanins','Plant-derived pigment blend','Fish','Published film study; no imported numerical curve',
       'A 2020 film study investigated combined curcumin and anthocyanin indicators for fish freshness.',
       'A combination of pigments is not represented by one pKa. A reproducible optical model requires measurements of that exact film.',
       'https://doi.org/10.1016/j.foodhyd.2019.105438','none','2020 - Curcumin/anthocyanin fish freshness film','#985D62','Mixed curcumin and anthocyanin indicator film'),

]

BY_ID = {i.id:i for i in INDICATORS}

def get_indicator(indicator_id:str)->Indicator:
    if indicator_id not in BY_ID:
        raise ValueError('Unknown indicator '+str(indicator_id))
    return BY_ID[indicator_id]


def measured_evidence(indicator_id:str, food:str='Fish')->tuple[pd.DataFrame,str,str]:
    """Measurement data with original units, NOT a calibration for arbitrary TellTag designs.

    Returns (table, x_axis, y_axis). An empty table explicitly means no digitized data.
    """
    if indicator_id=='cabbage':
        # From 2022 paper Section 3.4: delta E 8.70 at 12h and 26.04 at 24h at 25C.
        t=pd.DataFrame([
          {'Time (h)':12.0,'Measured colour difference (Delta E)':8.70,'Food':'Fish','Temperature (C)':25.0,'Published system':'Red cabbage puree/PVA film','Source':BY_ID[indicator_id].url},
          {'Time (h)':24.0,'Measured colour difference (Delta E)':26.04,'Food':'Fish','Temperature (C)':25.0,'Published system':'Red cabbage puree/PVA film','Source':BY_ID[indicator_id].url},
        ])
        return t,'Time (h)','Measured colour difference (Delta E)'
    if indicator_id=='anthobeta':
        df=pd.read_csv(DATA/'food_film_colour_measurements.csv')
        target = 'Beef' if food=='Beef' else 'Fish (species unspecified in study)'
        df=df[(df['food']==target) & (df['storage_C']==4)].copy()
        if df.empty:return pd.DataFrame(),'',''
        t=pd.DataFrame({'Storage day':df.storage_day.astype(int),
          'Measured colour difference (Delta E)':df.measured_delta_E.astype(float),
          'Measurement SD':df.delta_E_sd.astype(float),
          'Food':df.food,'Temperature (C)':df.storage_C,
          'Published system':df.indicator,'Source':df.source_url})
        return t,'Storage day','Measured colour difference (Delta E)'
    return pd.DataFrame(),'',''


def research_summary(indicator_id:str,food:str)->dict:
    ind=get_indicator(indicator_id)
    df, x,y=measured_evidence(indicator_id,food)
    matches_food=food in ind.studied_on
    if indicator_id=='anthobeta' and food=='Chicken':
        matches_food=False
    status = 'Quantitative published points (different research film)' if not df.empty else 'Literature description; no matched numeric series imported'
    caution = ('The measurement refers to the chosen food and research film, not TellTag.' if matches_food else
               'Selected food does not match the published example; do not transfer the study result directly.')
    return {'name':ind.name,'status':status,'caution':caution,'source':ind.url,
            'points':len(df),'study':ind.source_name,'studied_on':ind.studied_on}
