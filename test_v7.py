import unittest
from dataclasses import replace
import numpy as np
from cost_model import Costs,estimate_costs,economic_break_even
from food_profiles import FOODS,food_reference,measured_points,assumed_gas_profile,quality_benchmark,indicator_evidence
from food_visual import food_svg,food_player
from model import Formulation,simulation
from reports_v7 import report_pdf,export_zip

class V7Tests(unittest.TestCase):
 def test_three_foods(self):self.assertEqual(set(FOODS),{'Beef','Chicken','Salmon'})
 def test_study_endpoints(self):
  for food in FOODS:
   frame=food_reference(food)
   actual=measured_points(food)
   self.assertAlmostEqual(frame['Food TVB-N (mg N/100g)'].iloc[0],float(actual.value.iloc[0]))
   self.assertAlmostEqual(frame['Food TVB-N (mg N/100g)'].iloc[-1],float(actual.value.iloc[-1]))
 def test_salmon_two_endpoint_warning_reality(self):
  self.assertEqual(len(measured_points('Salmon')),2)
  self.assertTrue(food_reference('Salmon')['Food bacteria (log CFU/g)'].isna().all())
 def test_beef_bacterial_benchmark_only(self):
  self.assertIsNotNone(quality_benchmark('Beef'))
  self.assertIsNone(quality_benchmark('Salmon'))
  self.assertAlmostEqual(quality_benchmark('Chicken'),312)
 def test_indicators_food_evidence(self):
  self.assertTrue('Direct chicken' in indicator_evidence('Chicken','BCP')[0])
  self.assertTrue('Direct salmon' in indicator_evidence('Salmon','SALMON_CDT')[0])
  self.assertTrue('Fish-family' in indicator_evidence('Salmon','BCP')[0])
 def test_assumed_profile_bounds(self):
  for food in FOODS:
   f=food_reference(food)
   p=assumed_gas_profile(food,f,2.,15.)
   self.assertAlmostEqual(p.headspace_ppm.iloc[0],2.)
   self.assertAlmostEqual(p.headspace_ppm.iloc[-1],15.)
 def test_assumed_profile_not_permitted_negative(self):
  with self.assertRaises(ValueError):assumed_gas_profile('Salmon',food_reference('Salmon'),5.,1.)
 def test_cost_area(self):
  a=estimate_costs(Costs(),25,100,95,4,1)
  b=estimate_costs(replace(Costs(),width_mm=50,height_mm=50),25,100,95,4,1)
  self.assertGreater(b['variable_cad_per_good_label'],a['variable_cad_per_good_label'])
 def test_thick_membrane_increases_cost(self):
  a=estimate_costs(Costs(),25,100,95,4,1)
  b=estimate_costs(Costs(),100,100,95,4,1)
  self.assertGreater(b['cost_cad_per_good_label'],a['cost_cad_per_good_label'])
 def test_thicker_matrix_increases_pigment_mass(self):
  a=estimate_costs(Costs(),25,50,95,4,1)
  b=estimate_costs(Costs(),25,150,95,4,1)
  self.assertAlmostEqual(b['indicator_mass_mg_per_label'],3*a['indicator_mass_mg_per_label'])
 def test_dye_pct_increases_cost(self):
  a=estimate_costs(Costs(),25,100,95,4,1)
  b=estimate_costs(Costs(),25,100,90,4,6)
  self.assertGreater(b['line_items_cad_per_label']['Indicator pigment'],a['line_items_cad_per_label']['Indicator pigment'])
 def test_batch_size_reduces_overhead(self):
  a=estimate_costs(replace(Costs(),batch_size=1000),25,100,95,4,1)
  b=estimate_costs(replace(Costs(),batch_size=100000),25,100,95,4,1)
  self.assertGreater(a['cost_cad_per_good_label'],b['cost_cad_per_good_label'])
 def test_higher_scrap_higher_cost(self):
  a=estimate_costs(replace(Costs(),scrap_fraction=0.),25,100,95,4,1)
  b=estimate_costs(replace(Costs(),scrap_fraction=.25),25,100,95,4,1)
  self.assertGreater(b['cost_cad_per_good_label'],a['cost_cad_per_good_label'])
 def test_bad_dry_composition(self):
  with self.assertRaises(ValueError):estimate_costs(Costs(),25,100,50,4,1)
 def test_zero_cost_reference_invalid(self):
  with self.assertRaises(ValueError):estimate_costs(replace(Costs(),reference_membrane_um=0),25,100,95,4,1)
 def test_break_even(self):
  e=economic_break_even(.05,8.,.28,.2)
  self.assertAlmostEqual(e['share_of_current_shrink_that_must_be_saved'],.05/(8*.28*.2))
 def test_food_images(self):
  for food in FOODS:
   txt=food_svg(food,'#442255',72,240,20,float('nan'),7,'Inside sealed package','BCP',True,True)
   self.assertIn(food.upper(),txt)
   self.assertIn('NOT A FRESHNESS OR SAFETY VERDICT',txt)
 def test_player(self):
  import pandas as pd
  txt=food_player('Salmon',pd.DataFrame({'hour':[0,24], 'tvbn':[10.,15.], 'gas':[0.,1.], 'dye':[0.,50.]}),'#FFDD00','#660077')
  self.assertIn('Play',txt)
  self.assertIn('SALMON',txt)
 def test_source_urls(self):
  for k,p in FOODS.items():self.assertTrue(p['source'].startswith('https://'))
 def test_sample_report_exports(self):
  ref=food_reference('Chicken');cost=estimate_costs(Costs(),25,100,95,4,1)
  record={'settings':{'food_type':'Chicken','indicator':'BCP','indicator_food_evidence':indicator_evidence('Chicken','BCP'),'membrane_material':'PET','membrane_um':25,'matrix_material':'Alginate','matrix_um':100,'composition':{'polymer_pct':95}},'results':{'midpoint_h_text':'Not reached','reference_benchmark_text':'13 d','timing_interpretation':'No measured headspace profile'},'cost_scenario':{'estimate':cost},'food_study_source':FOODS['Chicken']['source']}
  curve=simulation(Formulation('Demo'),n=5)
  pdf=report_pdf(record,curve,ref)
  self.assertTrue(pdf.startswith(b'%PDF'))
  zipdata=export_zip(record,curve,ref,measured_points('Chicken'))
  self.assertTrue(zipdata.startswith(b'PK'))

if __name__=='__main__':unittest.main()
