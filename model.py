"""TellTag V2: transparent, *uncalibrated* lumped gas-transport + dye model.

This is a comparative educational model; it is NOT a validated food-safety sensor.

Transport: R = sum(L_i / P_i), where P has units mol*m/(m^2*s*Pa)
            q_eq = S_area * p_gas, where S_area has units mol/(m^2*Pa)
            dq/dt = (p_gas - q / S_area) / R
            tau = R * S_area
Indicator: apparent_pH = starting_pH + q / buffer_capacity_area
           basic_fraction = 1 / (1 + 10**(pKa - apparent_pH))
The pH shift is a deliberately simplified *empirical* response relationship,
not an acid/base speciation calculation for a real multicomponent matrix.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd

ATM_PA = 101325.0


@dataclass(frozen=True)
class Formulation:
    name: str
    membrane_thickness_um: float = 50.0
    membrane_permeability_e15: float = 2.0
    matrix_thickness_um: float = 20.0
    matrix_permeability_e15: float = 10.0
    sorption_capacity_umol_m2_pa: float = 2.0
    buffer_capacity_umol_m2_ph: float = 3.0
    starting_ph: float = 5.4
    apparent_pka: float = 6.3
    acid_color: str = "#EBC44E"
    base_color: str = "#68428F"


def validate(formulation: Formulation) -> None:
    for field in (
        'membrane_thickness_um', 'membrane_permeability_e15',
        'matrix_thickness_um', 'matrix_permeability_e15',
        'sorption_capacity_umol_m2_pa', 'buffer_capacity_umol_m2_ph'
    ):
        if getattr(formulation, field) <= 0:
            raise ValueError(f'{field} must be greater than zero')
    for field in ('starting_ph', 'apparent_pka'):
        if not 0 <= getattr(formulation, field) <= 14:
            raise ValueError(f'{field} must be between 0 and 14')


def gas_resistance(formulation: Formulation, package_thickness_um=0.0,
                   package_permeability_e15=1.0) -> float:
    """Total resistance in Pa*s*m^2/mol, assuming 1-D series layers."""
    validate(formulation)
    r = (
        formulation.membrane_thickness_um * 1e-6
        / (formulation.membrane_permeability_e15 * 1e-15)
        + formulation.matrix_thickness_um * 1e-6
        / (formulation.matrix_permeability_e15 * 1e-15)
    )
    if package_thickness_um > 0:
        if package_permeability_e15 <= 0:
            raise ValueError('package_permeability_e15 must be positive')
        r += package_thickness_um * 1e-6 / (package_permeability_e15 * 1e-15)
    return r


def base_fraction(ph: np.ndarray | float, pka: float) -> np.ndarray:
    return 1.0 / (1.0 + np.power(10.0, pka - np.asarray(ph)))


def hex_mix(color_a: str, color_b: str, fraction: float) -> str:
    """Illustrative sRGB mixture: NOT a spectral optical prediction."""
    f = float(np.clip(fraction, 0, 1))
    a = np.array([int(color_a[j:j + 2], 16) for j in (1, 3, 5)])
    b = np.array([int(color_b[j:j + 2], 16) for j in (1, 3, 5)])
    rgb = np.rint((1 - f) * a + f * b).astype(int)
    return '#' + ''.join(f'{x:02X}' for x in rgb)


def simulation(
    formulation: Formulation,
    max_ppm: float = 30.0,
    duration_h: float = 72.0,
    profile: str = 'Constant exposure',
    package_thickness_um: float = 0.0,
    package_permeability_e15: float = 1.0,
    n: int = 289,
    measured_gas_profile: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Solve reversible lumped uptake under a constant or linear gas profile.

    Gas partial pressure is assumed to equal ppm(v) * 1e-6 * 1 atm.
    Over each short time step the analytic constant-pressure solution is used.
    The linear ramp uses the step midpoint to approximate driving pressure.
    """
    validate(formulation)
    if max_ppm < 0 or duration_h <= 0 or n < 2:
        raise ValueError('max_ppm >= 0, duration_h > 0, n >= 2 required')
    if profile not in ('Constant exposure', 'Linear increase', 'Uploaded gas profile'):
        raise ValueError('Unsupported profile')
    if profile == 'Uploaded gas profile' and measured_gas_profile is None:
        raise ValueError('Uploaded gas profile requires measured_gas_profile')
    if profile == 'Uploaded gas profile':
        from research import validate_gas_profile
        measured_gas_profile = validate_gas_profile(measured_gas_profile, duration_h)
    times_h = np.linspace(0, duration_h, n)
    dt_seconds = float((times_h[1] - times_h[0]) * 3600)
    resistance = gas_resistance(formulation, package_thickness_um, package_permeability_e15)
    sorption = formulation.sorption_capacity_umol_m2_pa * 1e-6
    buffer = formulation.buffer_capacity_umol_m2_ph * 1e-6
    tau_seconds = resistance * sorption
    q = np.zeros(n, dtype=float)
    ppm = np.zeros(n, dtype=float)
    for idx in range(n):
        if profile == 'Uploaded gas profile':
            ppm[idx] = float(np.interp(times_h[idx], measured_gas_profile['hours'], measured_gas_profile['headspace_ppm']))
        else:
            ppm[idx] = max_ppm if profile == 'Constant exposure' else max_ppm * times_h[idx] / duration_h
        if idx > 0:
            if profile == 'Uploaded gas profile':
                mid_ppm = float(np.interp((times_h[idx - 1] + times_h[idx])/2, measured_gas_profile['hours'], measured_gas_profile['headspace_ppm']))
            else:
                mid_ppm = max_ppm if profile == 'Constant exposure' else max_ppm * (times_h[idx - 1] + times_h[idx]) / (2 * duration_h)
            p_mid = ATM_PA * (mid_ppm / 1e6)
            q_eq = sorption * p_mid
            q[idx] = q_eq + (q[idx - 1] - q_eq) * np.exp(-dt_seconds / tau_seconds)
    ph = formulation.starting_ph + q / buffer
    basic = base_fraction(ph, formulation.apparent_pka)
    return pd.DataFrame({
        'Hours': times_h,
        'Headspace gas (ppm)': ppm,
        'Film uptake (umol/m2)': q * 1e6,
        'Apparent pH': ph,
        'Basic dye fraction (%)': basic * 100,
    })


def crossing_time_hours(df: pd.DataFrame, fraction_pct: float = 50.0) -> float | None:
    """First interpolation crossing of the basic-form threshold; None if never."""
    y = df['Basic dye fraction (%)'].to_numpy()
    x = df['Hours'].to_numpy()
    if y[0] >= fraction_pct:
        return 0.0
    indices = np.where(y >= fraction_pct)[0]
    if len(indices) == 0:
        return None
    j = int(indices[0])
    return float(np.interp(fraction_pct, [y[j-1], y[j]], [x[j-1], x[j]]))


def sensitivity_scan(formulation: Formulation, **simulation_kwargs) -> pd.DataFrame:
    """One-at-a-time assumption scan; NOT statistical confidence intervals."""
    factors = {
        'Membrane permeability': 'membrane_permeability_e15',
        'Matrix permeability': 'matrix_permeability_e15',
        'Film gas capacity': 'sorption_capacity_umol_m2_pa',
        'Apparent buffering': 'buffer_capacity_umol_m2_ph',
    }
    results = []
    for title, attr in factors.items():
        x = getattr(formulation, attr)
        lo = simulation(replace(formulation, **{attr: 0.75 * x}), **simulation_kwargs)['Basic dye fraction (%)'].iloc[-1]
        hi = simulation(replace(formulation, **{attr: 1.25 * x}), **simulation_kwargs)['Basic dye fraction (%)'].iloc[-1]
        results.append({'Parameter': title, 'Result at -25% (%)': round(lo, 1), 'Result at +25% (%)': round(hi, 1), 'Spread (percentage points)': round(abs(hi-lo), 1)})
    lo = simulation(replace(formulation, apparent_pka=max(0, formulation.apparent_pka - 0.25)), **simulation_kwargs)['Basic dye fraction (%)'].iloc[-1]
    hi = simulation(replace(formulation, apparent_pka=min(14, formulation.apparent_pka + 0.25)), **simulation_kwargs)['Basic dye fraction (%)'].iloc[-1]
    results.append({'Parameter': 'Apparent pKa (±0.25 units)', 'Result at -25% (%)': round(lo, 1), 'Result at +25% (%)': round(hi, 1), 'Spread (percentage points)': round(abs(hi-lo), 1)})
    return pd.DataFrame(results).sort_values('Spread (percentage points)', ascending=False).reset_index(drop=True)
