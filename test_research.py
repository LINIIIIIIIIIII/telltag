"""Tests for research tools; passing tests do NOT validate chemistry."""
import unittest
from dataclasses import replace
import pandas as pd
from model import Formulation, simulation
from research import (timing_scenario, validate_gas_profile,
                      compare_measured_basic_fraction, interpretation)

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.f = Formulation('test')
        self.model = simulation(self.f, max_ppm=30, duration_h=72)

    def test_gas_profile_start_and_duration_required(self):
        with self.assertRaises(ValueError):
            validate_gas_profile(pd.DataFrame({'hours':[1,24],'headspace_ppm':[1,10]}), 24)
        with self.assertRaises(ValueError):
            validate_gas_profile(pd.DataFrame({'hours':[0,23],'headspace_ppm':[1,10]}), 24)

    def test_gas_profile_rejects_invalid_units_or_duplicate(self):
        with self.assertRaises(ValueError):
            validate_gas_profile(pd.DataFrame({'hours':[0,24],'mg_per_L':[0,15]}), 24)
        with self.assertRaises(ValueError):
            validate_gas_profile(pd.DataFrame({'hours':[0,0,24],'headspace_ppm':[0,1,10]}), 24)
        with self.assertRaises(ValueError):
            validate_gas_profile(pd.DataFrame({'hours':[0,24],'headspace_ppm':[0,-10]}), 24)

    def test_uploaded_gas_zero_remains_zero(self):
        gas = pd.DataFrame({'hours':[0,72], 'headspace_ppm':[0,0]})
        out=simulation(self.f, duration_h=72, profile='Uploaded gas profile', measured_gas_profile=gas)
        self.assertAlmostEqual(out['Film uptake (umol/m2)'].iloc[-1],0)

    def test_uploaded_profile_step_vs_constant(self):
        gas=pd.DataFrame({'hours':[0,36,72], 'headspace_ppm':[0,0,30]})
        pulse=simulation(self.f, duration_h=72,profile='Uploaded gas profile',measured_gas_profile=gas)
        constant=simulation(self.f,max_ppm=30,duration_h=72)
        self.assertLess(pulse['Film uptake (umol/m2)'].iloc[-1],constant['Film uptake (umol/m2)'].iloc[-1])

    def test_timing_arithmetic_is_conditional(self):
        value=timing_scenario(self.model, quality_hour=48,lead_hour=6)
        self.assertEqual(value['latest_illustrative_crossing_hour'],42)
        self.assertIn('HYPOTHETICAL',value['status'])
        with self.assertRaises(ValueError):
            timing_scenario(self.model,quality_hour=6,lead_hour=6)

    def test_lab_comparison_same_quantity(self):
        obs=pd.DataFrame({'hours':[0,10,20,30,40], 'measured_basic_fraction_pct':[1,2,3,4,5]})
        result,metrics=compare_measured_basic_fraction(self.model,obs)
        self.assertEqual(metrics['Number of observations'],5)
        self.assertIn('MAE percentage points',metrics)
        self.assertEqual(len(result),5)
        with self.assertRaises(ValueError):
            compare_measured_basic_fraction(self.model,pd.DataFrame({'hours':[0,10,20,30,40], 'delta_E':[1,2,3,4,5]}))

    def test_no_percent_spoiled_claim(self):
        lines=interpretation(self.model, self.model)
        self.assertTrue(any('NOT the percent of spoiled food' in line for line in lines))

if __name__=='__main__':
    unittest.main()
