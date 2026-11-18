import unittest
import numpy as np
import pandas as pd
from beef_model import source_series,beef_reference,scenario_gas_profile,benchmark_time_hours,visual_progress_from_beef,compare_warning
from model import Formulation,simulation,crossing_time_hours
from reports_v6 import report_pdf,export_zip
from live_visual import live_beef_svg,timelapse_player

class TestBeefTimeline(unittest.TestCase):
 def test_measured_reference_endpoints(self):
  df=beef_reference()
  self.assertEqual(float(df['Beef bacteria (log CFU/g)'].iloc[0]),3.)
  self.assertEqual(float(df['Beef bacteria (log CFU/g)'].iloc[-1]),8.64)
  self.assertEqual(float(df['Beef TVB-N (mg N/100g)'].iloc[-1]),23.8)
 def test_benchmark(self):
  self.assertAlmostEqual(benchmark_time_hours()/24,6.1111111,places=4)
 def test_reference_is_interpolation(self):
  sample=source_series('TVB-N')
  ref=beef_reference()
  for _,r in sample.iterrows():
   i=np.argmin(abs(ref.Hours-r.day*24))
   self.assertAlmostEqual(float(ref['Beef TVB-N (mg N/100g)'].iloc[i]),float(r.value),places=8)
 def test_temperature_requires_opt_in(self):
  with self.assertRaises(ValueError):beef_reference(temp_c=10.)
 def test_q10_accelerates_study_equivalent_age(self):
  d=beef_reference(temp_c=14,use_assumed_q10=True,q10=2.)
  self.assertAlmostEqual(float(d['Study-equivalent age (h)'].iloc[100]),100.)
 def test_gas_is_bounded(self):
  b=beef_reference();g=scenario_gas_profile(b,end_ppm=7,start_ppm=.5)
  self.assertAlmostEqual(g.headspace_ppm.iloc[0],.5)
  self.assertAlmostEqual(g.headspace_ppm.iloc[-1],7.)
  self.assertTrue((g.headspace_ppm.diff().dropna()>=0).all())
 def test_gas_bridge_switch_changes_shape(self):
  d=beef_reference()
  a=scenario_gas_profile(d,bridge_metric='TVB-N',exponent=1)
  b=scenario_gas_profile(d,bridge_metric='Bacterial count',exponent=1)
  self.assertGreater(abs(a.headspace_ppm.iloc[220]-b.headspace_ppm.iloc[220]),.1)
 def test_invalid_params(self):
  with self.assertRaises(ValueError):scenario_gas_profile(beef_reference(),end_ppm=1,start_ppm=2)
 def test_film_thickness_changes_model(self):
  d=beef_reference();gas=scenario_gas_profile(d)
  a=simulation(Formulation('A',membrane_thickness_um=25),profile='Uploaded gas profile',measured_gas_profile=gas,duration_h=240)
  b=simulation(Formulation('B',membrane_thickness_um=100),profile='Uploaded gas profile',measured_gas_profile=gas,duration_h=240)
  self.assertLess(float(a['Basic dye fraction (%)'].iloc[250]),100.)
  self.assertGreater(float(a['Basic dye fraction (%)'].iloc[250]),float(b['Basic dye fraction (%)'].iloc[250]))
 def test_pka_effect(self):
  d=beef_reference();gas=scenario_gas_profile(d)
  a=simulation(Formulation('A',apparent_pka=6.3),profile='Uploaded gas profile',measured_gas_profile=gas,duration_h=240)
  b=simulation(Formulation('B',apparent_pka=7.1),profile='Uploaded gas profile',measured_gas_profile=gas,duration_h=240)
  self.assertGreater(float(a['Basic dye fraction (%)'].iloc[-1]),float(b['Basic dye fraction (%)'].iloc[-1]))
 def test_exposure_peak_effect(self):
  d=beef_reference()
  args={'duration_h':240,'profile':'Uploaded gas profile'}
  a=simulation(Formulation('A'),measured_gas_profile=scenario_gas_profile(d,end_ppm=7),**args)
  b=simulation(Formulation('B'),measured_gas_profile=scenario_gas_profile(d,end_ppm=15),**args)
  self.assertLess(float(a['Basic dye fraction (%)'].iloc[-1]),float(b['Basic dye fraction (%)'].iloc[-1]))
 def test_outside_package_slows_model(self):
  d=beef_reference();g=scenario_gas_profile(d)
  a=simulation(Formulation('A'),measured_gas_profile=g,profile='Uploaded gas profile',duration_h=240)
  b=simulation(Formulation('B'),measured_gas_profile=g,profile='Uploaded gas profile',duration_h=240,package_thickness_um=50,package_permeability_e15=1.)
  self.assertLess(float(b['Basic dye fraction (%)'].iloc[240]),float(a['Basic dye fraction (%)'].iloc[240]))
 def test_svg_has_safety_notice(self):
  svg=live_beef_svg('#deddee',120,.5,6.8,18.,7.,'Inside sealed package','BCP')
  self.assertIn('No food-safety',svg)
 def test_html_player_interactive(self):
  d=beef_reference();arr=pd.DataFrame({'hour':d.Hours,'bact':d['Beef bacteria (log CFU/g)'],'tvbn':d['Beef TVB-N (mg N/100g)'],'gas':np.linspace(0,7,len(d)),'dye':np.linspace(10,90,len(d))})
  html=timelapse_player(arr,'#af4653','#ecc84b','#6b428f')
  self.assertIn('Pause',html)
  self.assertIn('input type="range"',html)
 def test_pdf_and_zip(self):
  b=beef_reference();g=scenario_gas_profile(b)
  d=simulation(Formulation('X'),duration_h=240,profile='Uploaded gas profile',measured_gas_profile=g)
  record={'settings':{'indicator':'BCP','membrane_material':'PET','membrane_um':25,'matrix_material':'ALG','matrix_um':55,
  'placement':'Inside sealed package','package_um':0,'membrane_perm_e15':2,'matrix_perm_e15':10,
  'sorption':2,'buffering':3,'starting_ph':5.4,'pka':6.3,'composition':{},'exposure_mode':'beef','temperature_c':4,'humidity_pct':80,'gas_scenario':{}},
  'results':{'dye_model_applicable':True,'midpoint_h_text':'not reached','reference_benchmark_text':'6.1 d','timing_interpretation':'Hypothesis only'}}
  pdf=report_pdf(record,d,b)
  self.assertTrue(pdf.startswith(b'%PDF'))
  archive=export_zip(record,d,b,source_series('TVB-N'))
  self.assertTrue(archive.startswith(b'PK'))

if __name__=='__main__':unittest.main()
