"""Run with: python -m unittest -v test_model.py"""
import unittest
from dataclasses import replace
import numpy as np
from model import Formulation, simulation, crossing_time_hours, base_fraction, gas_resistance

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.f = Formulation(name='test')

    def test_zero_gas_no_ph_change(self):
        result = simulation(self.f, max_ppm=0)
        self.assertTrue(np.allclose(result['Apparent pH'], self.f.starting_ph))

    def test_zero_time_no_uptake(self):
        result = simulation(self.f)
        self.assertAlmostEqual(result['Film uptake (umol/m2)'].iloc[0], 0)

    def test_lower_membrane_permeability_slows_initial_response(self):
        slow = replace(self.f, membrane_permeability_e15=0.25)
        a = simulation(self.f)
        b = simulation(slow)
        self.assertGreater(a['Basic dye fraction (%)'].iloc[20], b['Basic dye fraction (%)'].iloc[20])

    def test_buffering_reduces_response(self):
        buffered = replace(self.f, buffer_capacity_umol_m2_ph=20)
        self.assertGreater(simulation(self.f)['Apparent pH'].iloc[-1],
                           simulation(buffered)['Apparent pH'].iloc[-1])

    def test_late_equilibrium_independent_of_membrane_permeability(self):
        f_fast = replace(self.f, membrane_permeability_e15=20)
        f_slow = replace(self.f, membrane_permeability_e15=1)
        a = simulation(f_fast, duration_h=10000)
        b = simulation(f_slow, duration_h=10000)
        self.assertAlmostEqual(a['Film uptake (umol/m2)'].iloc[-1],
                               b['Film uptake (umol/m2)'].iloc[-1], places=5)

    def test_henderson_hasselbalch_midpoint(self):
        self.assertAlmostEqual(float(base_fraction(6.3, 6.3)), 0.5)

    def test_thicker_package_slows_response(self):
        a = simulation(self.f)
        b = simulation(self.f, package_thickness_um=50, package_permeability_e15=0.2)
        self.assertLess(b['Film uptake (umol/m2)'].iloc[30], a['Film uptake (umol/m2)'].iloc[30])

    def test_crossing_is_none_for_zero_gas(self):
        self.assertIsNone(crossing_time_hours(simulation(self.f, max_ppm=0)))

    def test_resistance_scales_linearly_with_thickness(self):
        thin = replace(self.f, membrane_thickness_um=25)
        thick = replace(self.f, membrane_thickness_um=50)
        self.assertGreater(gas_resistance(thick), gas_resistance(thin))

if __name__ == '__main__':
    unittest.main()
