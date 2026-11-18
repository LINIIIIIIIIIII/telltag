"""Auditable CAD scenario-only material / production cost estimator.
All starter prices are DEMONSTRATION ASSUMPTIONS, not supplier quotes.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict

@dataclass
class Costs:
    width_mm:float=25.
    height_mm:float=25.
    membrane_cad_m2:float=2.0
    reference_membrane_um:float=25.0
    viewing_cad_m2:float=2.0
    adhesive_cad_m2:float=3.0
    adhesive_coverage:float=.3
    dry_matrix_density_kg_m3:float=1100.
    polymer_cad_kg:float=25.
    plasticizer_cad_kg:float=15.
    indicator_cad_g:float=3.0
    print_cad_label:float=.012
    assembly_cad_label:float=.020
    individual_packaging_cad_label:float=.008
    extra_testing_cad_batch:float=250.
    setup_tooling_cad_batch:float=600.
    scrap_fraction:float=.10
    batch_size:int=10000


def estimate_costs(inp:Costs,membrane_um:float,matrix_um:float,
                   polymer_pct:float,plasticizer_pct:float,indicator_pct:float,
                   viewing:bool=True,adhesive:bool=True)->dict:
    """area m2 = mm2 / 1e6. mass_g = m2 * µm*1e-6 * kg/m3 * 1000.
    Variable spend is scaled by 1/(1-scrap). Batch costs divide by sellable labels.
    Cost is NOT a vendor quote or proof of manufacturability.
    """
    if min(inp.width_mm,inp.height_mm,membrane_um,matrix_um,inp.batch_size,inp.dry_matrix_density_kg_m3,inp.reference_membrane_um)<=0:raise ValueError('All dimensions and batch quantities must be positive')
    if not 0<=inp.scrap_fraction<1:raise ValueError('Invalid scrap fraction')
    if not 0<=inp.adhesive_coverage<=1:raise ValueError('Invalid adhesive coverage')
    if min(polymer_pct,plasticizer_pct,indicator_pct)<0 or abs(sum([polymer_pct,plasticizer_pct,indicator_pct])-100)>1e-6:raise ValueError('Dry composition must total 100%')
    data=asdict(inp)
    if any(v<0 for k,v in data.items() if k not in ['scrap_fraction','adhesive_coverage']):raise ValueError('Negative price or input')
    area=inp.width_mm*inp.height_mm/1e6
    matrix_mass_g=area*matrix_um*1e-6*inp.dry_matrix_density_kg_m3*1000
    cost={
      'Membrane film':area*inp.membrane_cad_m2*(membrane_um/inp.reference_membrane_um),
      'Viewing film':area*inp.viewing_cad_m2 if viewing else 0.,
      'Adhesive':area*inp.adhesive_cad_m2*inp.adhesive_coverage if adhesive else 0.,
      'Matrix polymer':matrix_mass_g*(polymer_pct/100)*inp.polymer_cad_kg/1000,
      'Matrix plasticizer':matrix_mass_g*(plasticizer_pct/100)*inp.plasticizer_cad_kg/1000,
      'Indicator pigment':matrix_mass_g*(indicator_pct/100)*inp.indicator_cad_g,
      'Printing':inp.print_cad_label,
      'Assembly':inp.assembly_cad_label,
      'Individual packaging':inp.individual_packaging_cad_label}
    variable=sum(cost.values())/(1-inp.scrap_fraction)
    fixed=(inp.extra_testing_cad_batch+inp.setup_tooling_cad_batch)/inp.batch_size
    final=variable+fixed
    return {'cost_cad_per_good_label':final,'variable_cad_per_good_label':variable,
      'batch_fixed_cad_per_label':fixed,'total_cad_per_batch':final*inp.batch_size,
      'line_items_cad_per_label':{**{k:v/(1-inp.scrap_fraction) for k,v in cost.items()},'Batch setup & testing':fixed},
      'material_mass_g_per_label':matrix_mass_g,'indicator_mass_mg_per_label':matrix_mass_g*indicator_pct/100*1000,
      'area_m2_per_label':area,'inputs':data,'evidence':'All starter unit prices are hypothetical editable scenarios, not sourced supplier quotations.'}


def economic_break_even(label_cad:float,pack_cad:float,margin_fraction:float,shrink_fraction:float):
    if pack_cad<=0 or not 0<margin_fraction<=1 or not 0<shrink_fraction<=1:raise ValueError('Economic assumptions outside bounds')
    return {'saved_pack_margin_cad':pack_cad*margin_fraction,
            'share_of_current_shrink_that_must_be_saved':label_cad/(shrink_fraction*pack_cad*margin_fraction),
            'shrink_percentage_points_to_save':100*label_cad/(pack_cad*margin_fraction)}
