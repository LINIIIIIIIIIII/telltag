"""Research support utilities for TellTag. These do not establish food safety."""
from __future__ import annotations
import numpy as np
import pandas as pd
from model import crossing_time_hours

CANADA_STORAGE = [
    {'Food': 'Beef (raw)', 'Days from': 2, 'Days to': 4},
    {'Food': 'Pork (raw)', 'Days from': 2, 'Days to': 4},
    {'Food': 'Ground meat (raw)', 'Days from': 1, 'Days to': 2},
    {'Food': 'Chicken/turkey pieces (raw)', 'Days from': 2, 'Days to': 3},
    {'Food': 'Cod/salmon (raw)', 'Days from': 3, 'Days to': 4},
]
CANADA_STORAGE_URL = 'https://www.canada.ca/en/health-canada/services/general-food-safety-tips/safe-food-storage.html'
EU_TVBN_URL = 'https://eur-lex.europa.eu/legal-content/en/TXT/?uri=CELEX:32019R0627'
FOOD_REVIEW_URL = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11394942/'
FAO_URL = 'https://www.fao.org/4/v7180e/v7180e09.htm'
FOOD_CONTACT_URL = 'https://www.canada.ca/en/health-canada/services/food-nutrition/food-safety/packaging-materials.html'


def timing_scenario(df: pd.DataFrame, quality_hour: float, lead_hour: float,
                    threshold_pct: float = 50.0) -> dict:
    """Conditional timing arithmetic only; quality_hour is a hypothetical user assumption."""
    if quality_hour <= 0 or lead_hour < 0 or lead_hour >= quality_hour:
        raise ValueError('The quality-limit time must be greater than the lead time and zero.')
    if not 0 <= threshold_pct <= 100:
        raise ValueError('Model dye threshold must be from 0 to 100%.')
    t = crossing_time_hours(df, threshold_pct)
    latest = quality_hour - lead_hour
    return {
        'model_crossing_hour': t,
        'hypothetical_quality_hour': quality_hour,
        'required_lead_hour': lead_hour,
        'latest_illustrative_crossing_hour': latest,
        'conditional_margin_hours': None if t is None else float(latest - t),
        'model_earlier_than_illustrative_target': False if t is None else bool(t <= latest),
        'status': 'HYPOTHETICAL_ONLY_NO_FOOD_QUALITY_INFERENCE'
    }


def validate_gas_profile(frame: pd.DataFrame, duration_h: float) -> pd.DataFrame:
    """Only properly labeled gas-phase ppm by time; not solution mg/L or TVB-N."""
    expected = ['hours', 'headspace_ppm']
    if not set(expected).issubset(frame.columns):
        raise ValueError('CSV needs columns: hours,headspace_ppm')
    data = frame.loc[:, expected].copy()
    for col in expected:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    if len(data) < 2 or data.isna().any().any():
        raise ValueError('Provide at least 2 complete numeric rows.')
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError('All values must be finite.')
    if (data < 0).any().any():
        raise ValueError('Negative concentrations or times are invalid.')
    data = data.sort_values('hours').reset_index(drop=True)
    if data.hours.duplicated().any():
        raise ValueError('Duplicate times are not supported.')
    if data.hours.iloc[0] != 0 or data.hours.iloc[-1] < duration_h:
        raise ValueError('Measured profile must start at 0 h and cover the full simulation duration.')
    return data


def compare_measured_basic_fraction(model: pd.DataFrame, observed: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Compare same physical quantity only: lab-measured basic dye fraction, not delta E."""
    expected = ['hours', 'measured_basic_fraction_pct']
    if not set(expected).issubset(observed.columns):
        raise ValueError('CSV needs columns: hours,measured_basic_fraction_pct')
    data = observed.loc[:, expected].copy()
    for col in expected:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    if len(data) < 5 or data.isna().any().any() or not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError('Need 5 or more complete finite numeric measurements.')
    if (data.hours < 0).any() or (data.hours > float(model.Hours.iloc[-1])).any():
        raise ValueError('All observation times must fall within the simulation.')
    if ((data.measured_basic_fraction_pct < 0) | (data.measured_basic_fraction_pct > 100)).any():
        raise ValueError('Measured fractions must be within 0 to 100%.')
    if data.hours.nunique() < 5:
        raise ValueError('Need at least 5 distinct observation times.')
    data = data.sort_values('hours').reset_index(drop=True)
    data['simulated_basic_fraction_pct'] = np.interp(data.hours, model.Hours, model['Basic dye fraction (%)'])
    data['error_percentage_points'] = data['simulated_basic_fraction_pct'] - data['measured_basic_fraction_pct']
    err = data['error_percentage_points'].to_numpy()
    return data, {
        'MAE percentage points': float(np.mean(np.abs(err))),
        'RMSE percentage points': float(np.sqrt(np.mean(err**2))),
        'Number of observations': len(data),
        'status': 'MATCHED-CONDITIONS-COMPARISON_ONLY_NOT_INDEPENDENT_VALIDATION_AUTOMATICALLY'
    }


def interpretation(df: pd.DataFrame, baseline: pd.DataFrame) -> list[str]:
    t = crossing_time_hours(df)
    b = crossing_time_hours(baseline)
    ending = float(df['Basic dye fraction (%)'].iloc[-1])
    start = float(df['Basic dye fraction (%)'].iloc[0])
    sentences = [
        f'The model predicts {ending:.1f}% of the indicator dye is in its basic form at the end (it started at {start:.1f}%). This is NOT the percent of spoiled food.',
        ('The model first reaches its arbitrary 50% dye reference at '+f'{t:.1f} hours.' if t is not None else 'The dye never reaches the arbitrary 50% reference during this run.'),
        'The displayed colour is a visual blend, not a measured spectrum or a real sticker colour calibration.',
    ]
    if t is not None and b is not None:
        diff = t-b
        if abs(diff) < 0.05:
            sentences.append('Your design and demonstration baseline cross at approximately the same time in this scenario.')
        elif diff > 0:
            sentences.append(f'Your design crosses about {diff:.1f} hours later than the unverified baseline in the assumed model.')
        else:
            sentences.append(f'Your design crosses about {-diff:.1f} hours earlier than the unverified baseline in the assumed model.')
    sentences.append('No claim about real meat shelf life or food safety follows from this graph without measured gas profiles and validation.')
    return sentences
