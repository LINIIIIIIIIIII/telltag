"""Compare runs and extracted data integrity. Passing does NOT validate chemistry."""
import unittest
from dataclasses import replace
from pathlib import Path
import pandas as pd
from model import Formulation, simulation
from compare_runs import snapshot, describe_delta

DATA=Path(__file__).parent/'data'
class ComparisonTests(unittest.TestCase):
    def make(self,form=None,food='Beef',duration=72):
        f=form or Formulation('Test')
        conditions={'max_ppm':30.,'duration_h':duration,'profile':'Constant exposure','package_thickness_um':0.,'package_permeability_e15':1.}
        return snapshot(f,simulation(f,**conditions),conditions,{'food':food,'placement':'Inside sealed package','viewing':True,'adhesive':True})
    def test_identical_run(self):
        old=self.make();delta,summary=describe_delta(old,old)
        self.assertEqual(len(delta),0)
        self.assertTrue(any('not changed' in x for x in summary))
    def test_membrane_difference_detected(self):
        old=self.make();new=self.make(replace(Formulation('Test'),membrane_thickness_um=100))
        change,summary=describe_delta(old,new)
        self.assertIn('Membrane thickness',change.Setting.tolist())
        self.assertTrue(any('model reaches' in x for x in summary))
        self.assertTrue(any('not proof' in x.lower() or 'not' in x.lower() for x in summary))
    def test_food_is_visual_only(self):
        old=self.make();new=self.make(food='Chicken')
        change,summary=describe_delta(old,new)
        self.assertEqual(change['Impact type'].iloc[0],'visual only')
        self.assertTrue(any('Only visual' in x for x in summary))
    def test_multiple_changes_warns_against_causality(self):
        old=self.make();new=self.make(replace(Formulation('Test'),membrane_thickness_um=75,starting_ph=6))
        _,summary=describe_delta(old,new)
        self.assertTrue(any('multiple inputs' in x for x in summary))
    def test_measured_food_csv_has_sources_and_valid_units(self):
        data=pd.read_csv(DATA/'food_spoilage_measurements.csv')
        self.assertTrue({'BEEF_2025','CHICKEN_2026','SALMON_2017'} <= set(data.study_id))
        self.assertTrue(data.source_url.str.startswith('https://').all())
        self.assertFalse(data.value.isna().any())
        self.assertFalse('ppm' in set(data.unit))
        be=data[(data.study_id=='BEEF_2025') & (data.measurement=='Total bacterial count')]
        self.assertEqual(len(be),6)
        self.assertEqual(float(be.loc[be.day==6,'value'].iloc[0]),6.92)
        ch=data[(data.study_id=='CHICKEN_2026') & (data.measurement=='TVB-N')]
        self.assertEqual(float(ch.loc[ch.day==13,'value'].iloc[0]),20.80)
        salmon=data[(data.study_id=='SALMON_2017')]
        self.assertEqual(len(salmon),2)
if __name__=='__main__': unittest.main()
