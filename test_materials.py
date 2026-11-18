import unittest
from materials import (load_materials,role_ids,material,starting_thickness,
    thickness_summary,validate_dry_composition,readiness)
from material_visual import svg_stack

class MaterialsTests(unittest.TestCase):
    def test_catalog_is_large_sourced_and_ids_unique(self):
        d=load_materials()
        self.assertGreaterEqual(len(d),20)
        self.assertEqual(d.id.nunique(),len(d))
        self.assertTrue(d.source_url.str.startswith('https://').all())
    def test_no_unjustified_gas_specific_numbers(self):
        d=load_materials()
        self.assertTrue((d['measured_ammonia_permeability_SI']=='').all())
        self.assertTrue((d['measured_trimethylamine_permeability_SI']=='').all())
    def test_default_materials_have_right_roles(self):
        self.assertIn('RCL',role_ids('membrane'))
        self.assertIn('ALG',role_ids('matrix'))
        self.assertIn('PET',role_ids('window'))
        self.assertIn('PSA',role_ids('adhesive'))
    def test_supplier_min_is_not_theoretical_min(self):
        self.assertIn('Not a universal minimum',thickness_summary('BOPP'))
        self.assertIn('No verified thickness',thickness_summary('LDPE'))
        self.assertEqual(starting_thickness('RCL'),28)
    def test_virtual_composition_and_readiness(self):
        self.assertTrue(validate_dry_composition(95,4,1)[0])
        self.assertFalse(validate_dry_composition(94,4,1)[0])
        status,issues=readiness(['RCL','ALG'],False)
        self.assertIn('NOT a validated',status)
        self.assertTrue(any('permeability' in q for q in issues))
    def test_visual_text_escapes(self):
        html=svg_stack([('Indicator','Alginate <script>','test')],'#ccafad')
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)

if __name__=='__main__': unittest.main()
