"""TellTag V7 — multi-food research scenarios and auditable sticker economics.

ALL curves are unvalidated TellTag predictions. A measured reference beef study is
used only for food trajectories; ppm values come from an openly labelled bridge.
"""
from __future__ import annotations
from dataclasses import asdict,replace
from pathlib import Path
from io import BytesIO
import json
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from model import Formulation,simulation,crossing_time_hours,hex_mix,sensitivity_scan
from materials import material,role_ids,starting_thickness,load_materials,thickness_summary,validate_dry_composition
from indicators import INDICATORS,measured_evidence
from food_profiles import FOODS, MARKERS, food_reference, measured_points, assumed_gas_profile, quality_benchmark, food_index, indicator_evidence
from food_visual import food_svg,food_player
from research import validate_gas_profile,compare_measured_basic_fraction
from reports_v7 import report_pdf,report_text,export_zip
from cost_model import Costs, estimate_costs, economic_break_even

DATA=Path(__file__).parent/'data'
st.set_page_config(page_title='TellTag | Research Simulator V7',page_icon='🟩',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>.block-container{max-width:1420px;padding-top:1.5rem}
[data-testid="stMetric"]{background:#f6faf5;border:1px solid #dce7d9;border-radius:12px;padding:12px 16px}
[data-testid="stSidebar"]{background:#f5f7f2}h1,h2,h3{letter-spacing:-.03em}
h1{color:#264e3b!important}div.stButton button{border-radius:9px}</style>''',unsafe_allow_html=True)
st.caption('TELLTAG  /  EVIDENCE + MATERIALS + COST  /  V7')
st.title('Design a sticker. Explore food studies. Estimate cost.')
st.warning('**Not a validated digital twin or food-safety device.** Published food measurements are real, but the food → headspace-gas link and TellTag colour response are still assumptions. Costs start with illustrative prices, not quotes.')

INDICATORS={
 'BCP':{'name':'Bromocresol purple','pka':6.3,'acid':'#EBC44E','base':'#68428F',
  'source':'https://pubchem.ncbi.nlm.nih.gov/compound/8273','evidence':'Aqueous pKa and yellow/purple transition published; film-specific pKa and kinetic response are NOT measured.'},
 'BTB':{'name':'Bromothymol blue','pka':7.1,'acid':'#EBC44E','base':'#2A6AAB',
  'source':'https://www.sigmaaldrich.com/US/en/product/sigma/18470','evidence':'Aqueous indicator transition 6.0–7.6 reported; approximate pKa 7.1 is NOT a verified film value.'},
 'BCG':{'name':'Bromocresol green','pka':4.7,'acid':'#EBC44E','base':'#32748B',
  'source':'https://amyd.quimica.unam.mx/pluginfile.php/3312/mod_resource/content/0/Libro%20Harvey.%20Qu%C3%ADmica%20Anal%C3%ADtica.pdf','evidence':'Aqueous range 3.8–5.4; approximate pKa 4.7 is NOT a verified film value.'},
}

for item in __import__('indicators').INDICATORS:
    INDICATORS[item.id]={'name':item.name,'pka':None,'acid':item.sample_colour,'base':item.sample_colour,
                        'source':item.url,'evidence':item.finding+' NOTE: '+item.main_limit}

# Published multi-dye / selective probe research is listed for evidence only.
# A single apparent pKa is not an honest model for these systems.
INDICATORS.update({
 'BCP_CR':{'name':'Bromocresol purple + cresol red (fish research)','pka':None,'acid':'#D9DDD6','base':'#D9DDD6',
           'source':'https://pmc.ncbi.nlm.nih.gov/articles/PMC10177749/',
           'evidence':'A dual-dye mixture tested in a fish indicator study. Exact salmon response in TellTag not calibrated.'},
 'BCP_MR':{'name':'Bromocresol purple + methyl red (chicken research)','pka':None,'acid':'#D9DDD6','base':'#D9DDD6',
           'source':'https://www.mdpi.com/2304-8158/11/21/3533',
           'evidence':'A dual-indicator chicken study. Its film response cannot be reduced to a single pKa.'},
 'SALMON_CDT':{'name':'Salmon multi-amine research probe (CDT)','pka':None,'acid':'#D9DDD6','base':'#D9DDD6',
           'source':'https://www.sciencedirect.com/science/article/pii/S0003267025009195',
           'evidence':'A salmon-specific research sensor using colorimetric and fluorescent responses. Not a validated TellTag component or an established food-contact ingredient.'}
})


def reset_mem(): st.session_state.v6_mem_um=starting_thickness(st.session_state.v6_mem_id)
def reset_matrix(): st.session_state.v6_matrix_um=starting_thickness(st.session_state.v6_matrix_id)
def reset_indicator():
    x=INDICATORS[st.session_state.v6_indicator_id]
    st.session_state.v6_pka=float(x['pka'] or 6.3)
    st.session_state.v6_acid_color=x['acid'];st.session_state.v6_base_color=x['base']
def preset_mini():st.session_state.v6_mem_um=25

def preset_default():st.session_state.v6_mem_um=50

def preset_thick():st.session_state.v6_mem_um=100

with st.sidebar:
    st.subheader('1. Choose what to simulate')
    food_type=st.selectbox('Choose food',['Beef','Chicken','Salmon'],help='Each food uses a separate study with its own measured trend and packaging.')
    mode=st.selectbox('Exposure mode',['Food study + estimated gas','Constant gas exposure','Increasing gas exposure','Upload measured gas profile'],help="Study mode follows measured food TVB-N, but the conversion to headspace ppm is assumed.")
    if mode=='Food study + estimated gas':
        fp=FOODS[food_type]
        st.caption(f"**{food_type} study:** {fp['package']} at 4°C; {fp['measurement_count']} TVB-N observations.")
        duration_h=fp['days']*24
        temp_c=4.0
        use_q10=False;q10=2.0
        st.caption('Reference temperature fixed at the measured 4°C; no unvalidated temperature extrapolation.')
        bridge=st.selectbox('Gas assumption follows', ['TVB-N','Bacterial count'] if food_type=='Beef' else ['TVB-N'])
        gas_floor=st.number_input('Assumed starting headspace gas (ppm)',0.,50.,0.,.25)
        gas_peak=st.number_input('Assumed headspace gas at study endpoint (ppm)',min_value=gas_floor,max_value=1000.,value=max(7.,gas_floor),step=1.,help='This is hypothetical, NOT an observed gas concentration for the selected food.')
        bridge_shape=st.slider('Assumed gas buildup shape',.3,3.,1.,.1)
        st.markdown(f"[Open the original {food_type.lower()} study]({fp['source']})")
        if food_type=='Salmon':st.warning('Salmon research dataset here has only two TVB-N endpoints. The line between them is an illustration, not observed daily deterioration.')
    else:
        duration_h=st.slider('Duration (hours)',12,240,72,6)
        temp_c=st.number_input('Temperature (°C; recorded only)',-2.,30.,4.,1.)
        use_q10=False;q10=2.;bridge=None;gas_floor=0.;gas_peak=0.;bridge_shape=1.
        if mode!='Upload measured gas profile':
            gas_peak=st.number_input('Gas exposure maximum (ppm)',0.,1000.,30.,2.)
    st.divider();st.subheader('2. Context')
    gas_species=st.selectbox('Gas species (record only)',['Generic basic vapour','Ammonia (NH3)','Trimethylamine (TMA)','Dimethylamine (DMA)'],help='The current uptake equation does not distinguish species; measured species-dependent transport data is still required.')
    rh=st.slider('Relative humidity (%)',0,100,80,5)
    humidity_slope=st.number_input('OPTIONAL assumed sorption sensitivity to humidity',-1.,3.,0.,.1,help='0 = RH does not affect chemistry; changing this to a nonzero value applies an assumed linear correction to sorption. Not measured.')
    threshold_pct=st.slider('Model dye midpoint to inspect (%)',5,95,50,5)
    st.caption('This percentage is a dye-state marker, not a meat quality limit.')

live, costing, compare, evidence, exports = st.tabs(['01  Live simulator','02  Price per sticker','03  Compare & explain','04  Food and indicator evidence','05  Export your report'])

with live:
    left,right=st.columns([.94,1.35],gap='large')
    with left:
        st.subheader('Build the proposed layers')
        with st.expander('A. Materials and thickness — controls the transport equation',expanded=True):
            membrane_id=st.selectbox('Gas-facing membrane',role_ids('membrane'),index=role_ids('membrane').index('RCL'),format_func=lambda k:material(k)['name'],key='v6_mem_id',on_change=reset_mem)
            matrix_id=st.selectbox('Sensing matrix / binder',role_ids('matrix'),index=role_ids('matrix').index('ALG'),format_func=lambda k:material(k)['name'],key='v6_matrix_id',on_change=reset_matrix)
            c1,c2,c3=st.columns(3)
            c1.button('Thin (25 µm)',on_click=preset_mini,use_container_width=True)
            c2.button('50 µm',on_click=preset_default,use_container_width=True)
            c3.button('Thick (100 µm)',on_click=preset_thick,use_container_width=True)
            if 'v6_mem_um' not in st.session_state: st.session_state.v6_mem_um=starting_thickness(membrane_id)
            if 'v6_matrix_um' not in st.session_state: st.session_state.v6_matrix_um=starting_thickness(matrix_id)
            membrane_um=st.number_input('Membrane thickness (µm)',1,500,step=1,key='v6_mem_um')
            st.caption(thickness_summary(membrane_id))
            matrix_um=st.number_input('Matrix thickness (µm)',1,500,step=1,key='v6_matrix_um')
            st.caption(thickness_summary(matrix_id))
            st.caption('The material name **does not automatically supply gas permeability**. Changing the name may reset example thickness; use measured permeability when available.')
        with st.expander('B. Indicator chemistry — changes the response when pKa model is supported',expanded=True):
            indicator_id=st.selectbox('Indicator',list(INDICATORS),format_func=lambda k:INDICATORS[k]['name'],key='v6_indicator_id',on_change=reset_indicator)
            info=INDICATORS[indicator_id]
            modeled=info['pka'] is not None
            st.caption(info['evidence'])
            evidence_level,evidence_note,evidence_url=indicator_evidence(food_type,indicator_id)
            st.info(f'**{food_type} evidence: {evidence_level}.** {evidence_note}')
            if evidence_url:st.markdown(f'[Read food-specific research]({evidence_url})')
            st.markdown(f'[Indicator source]({info["source"]})')
            if 'v6_pka' not in st.session_state:st.session_state.v6_pka=float(info['pka'] or 6.3)
            if 'v6_acid_color' not in st.session_state:st.session_state.v6_acid_color=info['acid']
            if 'v6_base_color' not in st.session_state:st.session_state.v6_base_color=info['base']
            starting_ph=st.number_input('Starting apparent film pH (assumed)',0.,14.,5.4,.1)
            pka=st.number_input('Apparent film pKa (assumed unless calibrated)',0.,14.,step=.1,key='v6_pka',disabled=not modeled)
            pc1,pc2=st.columns(2)
            acid_color=pc1.color_picker('Acid appearance (illustrative)',key='v6_acid_color')
            base_color=pc2.color_picker('Basic appearance (illustrative)',key='v6_base_color')
            if not modeled:st.info('This pigment has no valid one-pKa film response in the model. Its measured research evidence remains available, but a fake kinetic colour curve will NOT be drawn.')
        with st.expander('C. Detailed physics — all numeric values influence the what-if calculation',expanded=False):
            membrane_perm=st.number_input('Membrane permeability ×10⁻¹⁵ SI (assumed)',.001,10000.,2.,.1,format='%.3f')
            matrix_perm=st.number_input('Matrix permeability ×10⁻¹⁵ SI (assumed)',.001,10000.,10.,.5,format='%.3f')
            sorption=st.number_input('Film gas uptake capacity µmol/m²/Pa (assumed)',.001,10000.,2.,.1,format='%.3f')
            buffering=st.number_input('Film buffering µmol/m²/pH (assumed)',.001,10000.,3.,.1,format='%.3f')
            st.caption('These are editable effective model parameters, NOT measured properties of the named materials.')
        with st.expander('D. Package, viewing film, adhesive, and composition',expanded=False):
            placement=st.radio('Sticker placement',['Inside sealed package','Outside sealed package'],horizontal=True)
            package_um=st.number_input('Existing package thickness (µm, outside only)',1.,500.,50.,1.,disabled=placement=='Inside sealed package')
            package_perm=st.number_input('Existing package gas permeability ×10⁻¹⁵ SI (outside only)',.001,1000.,1.,.1,disabled=placement=='Inside sealed package')
            viewing=st.checkbox('Include viewing layer',True)
            adhesive=st.checkbox('Include edge adhesive',True)
            window_id=st.selectbox('Viewing film',role_ids('window'),index=role_ids('window').index('PET'),format_func=lambda k:material(k)['name'],disabled=not viewing)
            glue_id=st.selectbox('Adhesive',role_ids('adhesive'),index=role_ids('adhesive').index('PSA'),format_func=lambda k:material(k)['name'],disabled=not adhesive)
            st.caption('Viewing/adhesive materials affect the assembly drawing and materials export; they do NOT change transport until their own gas/optical/leak properties are measured.')
            st.markdown('**Virtual dry formulation record — not a lab mixing protocol**')
            poly_pct=st.number_input('Polymer % (dry solid)',0.,100.,95.,1.)
            plast_pct=st.number_input('Plasticizer % (dry solid)',0.,100.,4.,1.)
            dye_pct=st.number_input('Indicator % (dry solid)',0.,100.,1.,.5)
            comp_ok,comp_message=validate_dry_composition(poly_pct,plast_pct,dye_pct)
            st.caption(comp_message+' These proportions are recorded, not connected to actual measured optical/transport properties.')
        st.caption('**Input impact guide:** thickness, effective permeabilities, gas scenario, sorption, buffering, film pH and pKa affect the modeled response. Dye palette changes colour only. Material identity, adhesive composition, and gas species need lab-measured properties before a trustworthy chemistry effect can be calculated.')

    # ---------- Compute shared state after all controls above are instantiated ----------
    sorption_eff=max(.001,float(sorption)*(1+float(humidity_slope)*(rh-80)/100))
    sample=Formulation(name='Your TellTag concept',membrane_thickness_um=membrane_um,
        membrane_permeability_e15=membrane_perm,matrix_thickness_um=matrix_um,
        matrix_permeability_e15=matrix_perm,sorption_capacity_umol_m2_pa=sorption_eff,
        buffer_capacity_umol_m2_ph=buffering,starting_ph=starting_ph,apparent_pka=pka,
        acid_color=acid_color,base_color=base_color)
    external=placement=='Outside sealed package'
    source_food=None
    gas_scenario={}
    if mode=='Food study + estimated gas':
        source_food=food_reference(food_type,n=481)
        gas_csv=assumed_gas_profile(food_type,source_food,start_ppm=gas_floor,end_ppm=gas_peak,shape=bridge_shape,driver=bridge)
        gas_scenario={'bridge_metric':bridge,'assumed_start_ppm':gas_floor,'assumed_peak_ppm':gas_peak,'assumed_curve_exponent':bridge_shape,'food_study':FOODS[food_type]['source'],'food_study_packaging':FOODS[food_type]['package'],'headspace_ppm_is_measured':False}
        sim_profile='Uploaded gas profile'
    elif mode=='Upload measured gas profile':
        gas_upload=st.file_uploader('Measured headspace CSV (hours,headspace_ppm)',type=['csv'],key='v6_gas_file')
        gas_csv=None
        if gas_upload is not None:
            try:gas_csv=validate_gas_profile(pd.read_csv(gas_upload),duration_h)
            except Exception as ex:st.error(f'Invalid gas file: {ex}')
        sim_profile='Uploaded gas profile' if gas_csv is not None else 'Constant exposure'
        gas_scenario={'file_uploaded':gas_csv is not None}
    else:
        gas_csv=None
        sim_profile='Constant exposure' if mode=='Constant gas exposure' else 'Linear increase'
        gas_scenario={'assumed_max_ppm':gas_peak}
    kwargs={'max_ppm':gas_peak if gas_csv is None and mode!='Upload measured gas profile' else 0.,
            'duration_h':float(duration_h),'profile':sim_profile,'n':481,
            'package_thickness_um':float(package_um) if external else 0.,
            'package_permeability_e15':float(package_perm) if external else 1.}
    if gas_csv is not None:kwargs['measured_gas_profile']=gas_csv
    calculated=simulation(sample,**kwargs)
    display_curve=calculated.copy()
    if not modeled:display_curve['Basic dye fraction (%)']=np.nan
    cross=crossing_time_hours(calculated,threshold_pct) if modeled else None
    study_benchmark=quality_benchmark(food_type) if source_food is not None else None
    if source_food is None:warning_summary='Manual gas-only what-if calculation. No food-specific outcome.'
    elif study_benchmark is None:warning_summary=f'No independently supported benchmark time available from the loaded {food_type} reference. Cannot quantify early or late warning.'
    elif cross is None:warning_summary=f'The dye model did not reach the chosen midpoint during the {food_type} scenario.'
    else:warning_summary=f'What-if model threshold: {cross/24:.2f} days; separate {food_type} study benchmark: {study_benchmark/24:.2f} days. The assumed ppm link makes the comparison NOT a real prediction of warning accuracy.'

    with right:
        st.subheader(f'{food_type}: study timeline + simulated sticker')
        show_time=st.slider('Move through study time (hours)',0.,float(duration_h),float(duration_h)/2,.5,key='v7_time')
        gas=float(np.interp(show_time,calculated.Hours,calculated['Headspace gas (ppm)']))
        frac=float(np.interp(show_time,calculated.Hours,calculated['Basic dye fraction (%)'])) if modeled else float('nan')
        colour=hex_mix(acid_color,base_color,frac/100) if modeled else '#D9DDD6'
        tvbn=float(np.interp(show_time,source_food.Hours,source_food['Food TVB-N (mg N/100g)'])) if source_food is not None else float('nan')
        bacter=float(np.interp(show_time,source_food.Hours,source_food['Food bacteria (log CFU/g)'])) if source_food is not None and source_food['Food bacteria (log CFU/g)'].notna().any() else float('nan')
        components.html(food_svg(food_type,colour,show_time,duration_h,tvbn,bacter,gas,placement,info['name'],modeled,source_food is not None),height=330,scrolling=False)
        st.caption(f'{food_type} appearance and sticker colour are ILLUSTRATIONS. Study TVB-N readings are interpolated only for the timeline; gas ppm and dye state are uncalibrated assumptions.')
        if source_food is not None:
            with st.expander('▶ Play a food + sticker time-lapse',expanded=False):
                player_df=pd.DataFrame({'hour':source_food.Hours,'tvbn':source_food['Food TVB-N (mg N/100g)'],'gas':calculated['Headspace gas (ppm)'],'dye':display_curve['Basic dye fraction (%)']})
                components.html(food_player(food_type,player_df,acid_color,base_color if modeled else None),height=340,scrolling=False)
        a,b,c=st.columns(3)
        a.metric('What-if dye threshold',f'{cross/24:.1f} d' if cross is not None else 'Not reached')
        b.metric('Food-study benchmark',f'{study_benchmark/24:.1f} d' if study_benchmark is not None else 'Not established')
        c.metric('Assumed headspace ppm',f'{gas:.2f}')
        st.info(warning_summary)
        fig=go.Figure()
        if modeled:fig.add_trace(go.Scatter(x=calculated.Hours/24,y=calculated['Basic dye fraction (%)'],name='Hypothetical dye fraction',line=dict(color='#426c50',width=3)))
        else:fig.add_trace(go.Scatter(x=calculated.Hours/24,y=calculated['Headspace gas (ppm)'],name='Assumed headspace ppm',line=dict(color='#426c50',width=3)))
        fig.add_vline(x=show_time/24,line_dash='dot',line_color='#A3B1A5')
        fig.update_layout(title='Calculated sticker response (NOT laboratory validated)',xaxis_title='Study time (days)',yaxis_title='Modeled dye (%)' if modeled else 'Assumed gas (ppm)',height=320)
        st.plotly_chart(fig,use_container_width=True)
        if source_food is not None:
            with st.expander(f'View actual {food_type.lower()} study data vs. interpolation'):
                actual=measured_points(food_type,'TVB-N')
                fg=go.Figure()
                fg.add_trace(go.Scatter(x=actual.day,y=actual.value,mode='markers',marker=dict(size=11,color='#A57842'),name='Published measured points'))
                fg.add_trace(go.Scatter(x=source_food.Hours/24,y=source_food['Food TVB-N (mg N/100g)'],line=dict(dash='dash',color='#647D70'),name='Line between measurements (illustration)'))
                fg.update_layout(xaxis_title='Days',yaxis_title='TVB-N in food (mg N/100g)',height=300)
                st.plotly_chart(fg,use_container_width=True)
                st.caption('TVB-N in food is NOT headspace ppm. This is not a food-safety threshold.')


with costing:
    st.subheader('What might a finished sticker cost?')
    st.warning('**Every initial CAD input below is an illustrative scenario, not a supplier quote.** Replace prices with actual supplier quotes to make this estimate meaningful.')
    q1,q2,q3=st.columns(3)
    with q1:
        width=st.number_input('Sticker width (mm)',5.,100.,25.,1.)
        height=st.number_input('Sticker height (mm)',5.,100.,25.,1.)
        batch=st.selectbox('Production batch size',[1000,10000,100000,1000000],index=1)
        scrap=st.slider('Production loss / scrap (%)',0,60,10,1)
    with q2:
        mem_price=st.number_input('Membrane film (CAD/m² at reference thickness)',0.,1000.,2.,.5)
        mem_ref_um=st.number_input('Reference film thickness for this price (µm)',1.,500.,25.,1.,help='Cost is assumed to scale linearly with thickness. Real supplier film prices may not.')
        view_price=st.number_input('Viewing film (CAD per m²)',0.,1000.,2.,.5)
        adhesive_price=st.number_input('Adhesive film (CAD per m²)',0.,1000.,3.,.5)
        adhesive_coverage=st.slider('Adhesive coverage of sticker area (%)',0,100,30,5)
        density=st.number_input('Assumed dry matrix density (kg/m³)',300.,3000.,1100.,50.)
    with q3:
        polymer_price=st.number_input('Matrix polymer (CAD/kg)',0.,10000.,25.,1.)
        plasticizer_price=st.number_input('Plasticizer (CAD/kg)',0.,10000.,15.,1.)
        indicator_price=st.number_input('Selected dye / pigment (CAD/g)',0.,10000.,3.,.25)
        print_cost=st.number_input('Printing (CAD per label)',0.,10.,.012,.001,format='%.3f')
        labor_cost=st.number_input('Assembly (CAD per label)',0.,10.,.020,.001,format='%.3f')
        pack_cost=st.number_input('Individual packaging (CAD per label)',0.,10.,.008,.001,format='%.3f')
    with st.expander('Batch expenses + commercial viability',expanded=False):
        testing_cost=st.number_input('Testing / QC per batch (CAD)',0.,1000000.,250.,25.)
        setup_cost=st.number_input('Setup + tooling per batch (CAD)',0.,1000000.,600.,50.)
        pack_price=st.number_input('Food pack retail price (CAD; scenario)',.01,1000., {'Beef':9.,'Chicken':6.66,'Salmon':8.57}[food_type],.10)
        margin=st.slider('Assumed retail gross margin (%)',1,90,28,1)
        shrink=st.slider('Assumed discarded stock (%)',1,90,{'Beef':15,'Chicken':13,'Salmon':21}[food_type],1)
        st.caption('Retail prices are starting scenarios, informed by the project economics report; shrink and margin are proxies from different markets and years, not current retailer measurements.')
    cost_inputs=Costs(width_mm=width,height_mm=height,membrane_cad_m2=mem_price,reference_membrane_um=mem_ref_um,viewing_cad_m2=view_price,
                      adhesive_cad_m2=adhesive_price,adhesive_coverage=adhesive_coverage/100,
                      dry_matrix_density_kg_m3=density,polymer_cad_kg=polymer_price,plasticizer_cad_kg=plasticizer_price,
                      indicator_cad_g=indicator_price,print_cad_label=print_cost,assembly_cad_label=labor_cost,
                      individual_packaging_cad_label=pack_cost,extra_testing_cad_batch=testing_cost,
                      setup_tooling_cad_batch=setup_cost,scrap_fraction=scrap/100,batch_size=batch)
    if comp_ok:
        costing_result=estimate_costs(cost_inputs,membrane_um,matrix_um,poly_pct,plast_pct,dye_pct,viewing,adhesive)
        c1,c2,c3=st.columns(3)
        c1.metric('Estimated cost / sticker (CAD)',f"${costing_result['cost_cad_per_good_label']:.4f}")
        c2.metric('Whole batch estimate (CAD)',f"${costing_result['total_cad_per_batch']:,.2f}")
        c3.metric('Indicator loading (mg / sticker)',f"{costing_result['indicator_mass_mg_per_label']:.3f}")
        breakdown=pd.DataFrame([{'Cost item':k,'CAD per sticker':v} for k,v in costing_result['line_items_cad_per_label'].items()]).sort_values('CAD per sticker',ascending=False)
        st.dataframe(breakdown.style.format({'CAD per sticker':'${:.5f}'}),hide_index=True,use_container_width=True)
        sizes=[]
        for bs in (1000,10000,100000,1000000):
            inp=replace(cost_inputs,batch_size=bs)
            sizes.append({'Batch quantity':str(bs),'CAD / label':estimate_costs(inp,membrane_um,matrix_um,poly_pct,plast_pct,dye_pct,viewing,adhesive)['cost_cad_per_good_label']})
        st.plotly_chart(go.Figure(go.Bar(x=[x['Batch quantity'] for x in sizes],y=[x['CAD / label'] for x in sizes])).update_layout(title='How batch size changes assumed unit cost',xaxis_title='Finished labels',yaxis_title='CAD per label',height=310),use_container_width=True)
        econ=economic_break_even(costing_result['cost_cad_per_good_label'],pack_price,margin/100,shrink/100)
        share=econ['share_of_current_shrink_that_must_be_saved']
        st.write(f"Under these retail assumptions, the label would need to prevent the loss of **{share*100:.1f}% of currently discarded packs** to pay for itself using recovered gross margin only.")
        if share>1:st.error('This is over 100% of discarded packs: this business scenario cannot break even on recovered margin alone.')
        st.caption('Film costs are approximated as proportional to thickness. Real prices may not scale this way. These are not supplier quotations, measured shrink reduction, or permission to extend printed use-by dates.')
        cost_scenario={'inputs':asdict(cost_inputs),'estimate':costing_result,'retail_illustration':{'pack_price_cad':pack_price,'margin_pct':margin,'shrink_pct':shrink,'break_even':econ},'all_cost_inputs_are': 'user-editable demonstration assumptions, not supplier quotes'}
    else:
        st.error('Dry layer percentages must add up to 100% before costing.')
        cost_scenario={'error':'Dry composition not balanced'}
    st.download_button('Download cost breakdown (CSV)',pd.DataFrame([{'Cost item':k,'CAD per sticker':v} for k,v in cost_scenario.get('estimate',{}).get('line_items_cad_per_label',{}).items()]).to_csv(index=False),'TellTag_V7_Cost_Breakdown.csv','text/csv')
    st.download_button('Download cost assumptions (JSON)',json.dumps(cost_scenario,indent=2),'TellTag_V7_Cost_Inputs.json','application/json')

# Persistent run records during this app session.
settings={
 'food_type':food_type,'food_study_source':FOODS[food_type]['source'] if source_food is not None else None,
 'dye_fraction_threshold_pct':int(threshold_pct),'indicator':info['name'],'indicator_id':indicator_id,'indicator_source':info['source'],
 'membrane_material':material(membrane_id)['name'],'membrane_id':membrane_id,'membrane_um':int(membrane_um),
 'matrix_material':material(matrix_id)['name'],'matrix_id':matrix_id,'matrix_um':int(matrix_um),
 'membrane_perm_e15':float(membrane_perm),'matrix_perm_e15':float(matrix_perm),'sorption':float(sorption),
 'effective_sorption_after_assumed_humidity':sorption_eff,'buffering':float(buffering),
 'starting_ph':float(starting_ph),'pka':float(pka) if modeled else None,
 'acid_color':acid_color,'base_color':base_color,'placement':placement,
 'package_um':float(package_um) if external else 0.,'package_perm_e15':float(package_perm) if external else None,
 'viewing_material':material(window_id)['name'] if viewing else None,
 'adhesive_material':material(glue_id)['name'] if adhesive else None,
 'temperature_c':float(temp_c),'humidity_pct':int(rh),'assumed_humidity_response_slope':float(humidity_slope),
 'gas_species_record_only':gas_species,
 'composition':{'polymer_pct':poly_pct,'plasticizer_pct':plast_pct,'indicator_pct':dye_pct,'balanced':comp_ok},
 'exposure_mode':mode,'gas_scenario':gas_scenario,'indicator_food_evidence':indicator_evidence(food_type,indicator_id)}
result_fields={'dye_model_applicable':modeled,'midpoint_h':cross,
 'midpoint_h_text':f'{cross:.1f} h ({cross/24:.2f} days)' if cross is not None else 'Not reached / not modelled',
 'reference_benchmark_h':study_benchmark,'reference_benchmark_text':f'{study_benchmark:.1f} h ({study_benchmark/24:.2f} days)' if study_benchmark is not None else 'Not applicable',
 'timing_interpretation':warning_summary,'end_dye_fraction_pct':float(calculated['Basic dye fraction (%)'].iloc[-1]) if modeled else None}
record={'project':'TellTag','version':'V7','status':'RESEARCH-ONLY_UNCALIBRATED','settings':settings,'results':result_fields,
        'food_study_source':FOODS[food_type]['source'] if source_food is not None else None,'cost_scenario':cost_scenario,
        'exact_material_grade_kinetics_known':False,'safety_warning':'No inference of food safety or pathogen status'}

with compare:
    st.subheader('Compare with a previous design')
    st.write('Save the current settings, change one input in **Live simulator**, then return. The comparison will explain what actually changed.')
    if st.button('Save this design as the comparison baseline',type='primary'):
        st.session_state['v6_saved']={'record':record,'curve':calculated.copy()};st.success('Saved for this browser session. You can also export your data for a permanent record.')
    prev=st.session_state.get('v6_saved')
    if prev is None:st.info('Save a design first. Then change membrane thickness, pKa or another model input and compare.')
    else:
        old=prev['record'];prior=prev['curve'];current=record
        changes=[]
        for key,val in settings.items():
            earlier=old['settings'].get(key)
            if earlier!=val: changes.append({'Setting':key.replace('_',' '),'Before':str(earlier),'Now':str(val)})
        if changes: st.dataframe(pd.DataFrame(changes),use_container_width=True,hide_index=True)
        else:st.info('Settings are identical to the saved design.')
        old_cross=old['results'].get('midpoint_h');new_cross=cross
        a,b=st.columns(2)
        a.metric('Saved dye threshold',f'{old_cross:.1f} h' if old_cross is not None else 'Not reached')
        b.metric('Current dye threshold',f'{new_cross:.1f} h' if new_cross is not None else 'Not reached')
        if old_cross is not None and new_cross is not None:
            dt=new_cross-old_cross
            st.write(f'**Interpretation:** In the model, the current design reaches the selected model dye threshold **{abs(dt):.1f} h {"later" if dt>0 else "earlier" if dt<0 else "at the same time"}** than your saved design.')
        if len(changes)>1:st.warning('Several settings changed. You cannot attribute the difference to one variable.')
        fig2=go.Figure()
        if old['results']['dye_model_applicable']:
            fig2.add_trace(go.Scatter(x=prior.Hours/24,y=prior['Basic dye fraction (%)'],name='Saved design',line=dict(color='#b59c73')))
        if modeled:fig2.add_trace(go.Scatter(x=calculated.Hours/24,y=calculated['Basic dye fraction (%)'],name='Current design',line=dict(color='#2b6c50')))
        fig2.update_layout(xaxis_title='Days',yaxis_title='Basic dye fraction (%)',height=350)
        st.plotly_chart(fig2,use_container_width=True)
        st.caption('These are two mathematical what-if runs, not replicates of physical experiments.')
        st.download_button('Download comparison summary',json.dumps({'previous':old,'current':current,'changes':changes},indent=2),file_name='telltag_v6_comparison.json',mime='application/json')
    with st.expander('See which numerical inputs matter most (±25% scan)'):
        if modeled:
            st.dataframe(sensitivity_scan(sample,**kwargs),use_container_width=True,hide_index=True)
            st.caption('This is sensitivity to assumed parameters, not a statistical confidence interval.')
        else:st.info('No quantitative one-pKa indicator response for the selected pigment.')

with evidence:
    st.subheader(f'{food_type}: what the literature really measured')
    p=FOODS[food_type]
    st.write(f"**Study:** {p['name']} · {p['package']} · 4°C. {p['qual_source']}")
    st.markdown(f"[Original study]({p['source']})")
    st.warning('The study durations are not universal storage guidelines or evidence that food remains safe. A spoilage indicator also cannot detect pathogens reliably.')
    if source_food is not None:
        tv=measured_points(food_type,'TVB-N')
        st.dataframe(tv[['day','value','unit','source_url']],use_container_width=True,hide_index=True)
        st.download_button(f'Download measured {food_type.lower()} study points',tv.to_csv(index=False),f'TellTag_V7_{food_type}_Study_TVBN.csv','text/csv')
    st.markdown('**Which chemicals could be relevant?**')
    for name,explain,url in MARKERS[food_type]:
        st.write(f'**{name}:** {explain}')
        st.markdown(f'[Source]({url})')
    st.markdown('**Which indicator has evidence for this food?**')
    rows=[]
    for k,entry in INDICATORS.items():
        level,note,url=indicator_evidence(food_type,k)
        rows.append({'Indicator':entry['name'],'Evidence for this food':level,'Why':note,'Source':url})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    st.caption('Evidence for an indicator in a chicken study does not validate the same indicator for salmon; using another package also changes the gas environment.')
    st.markdown('**Material records are documented options, not approved completed food-contact labels.**')
    mat=load_materials()
    st.dataframe(mat[['name','roles','documented_low_um','documented_high_um','example_thickness_um','source_url']],use_container_width=True,hide_index=True)
    st.markdown('**Market context from your Drive research:** no verified public bulk price for a completed colour-changing spoilage label was established in that report. V7 calculates what-if costs, not actual market quotations.')
    st.markdown('[Open your original Telltag full research report](https://docs.google.com/document/d/1v-j2m8XzQJ_ZYsamB4C42fHiN5FoeD3-knU2Pbxo2c4/edit)')

with exports:
    st.subheader('Download results that actually explain the simulation')
    st.write('The report includes your exact settings, selected food reference, hypothetical sticker response, cost breakdown, assumptions and research citations.')
    p1,p2,p3=st.columns(3)
    with p1:st.metric('Model response',result_fields['midpoint_h_text'])
    with p2:st.metric('Beef reference',result_fields['reference_benchmark_text'])
    with p3:st.metric('Cost scenario / sticker',f"${cost_scenario.get('estimate',{}).get('cost_cad_per_good_label',float('nan')):.4f} CAD")
    try:
        pdf=report_pdf(record,calculated,source_food)
        packet=export_zip(record,calculated,source_food,measured_points(food_type,'TVB-N'))
        st.download_button('Download understandable PDF report',pdf,'TellTag_V7_Research_Report.pdf','application/pdf',type='primary')
        st.download_button('Download everything (ZIP)',packet,'TellTag_V7_Research_Packet.zip','application/zip')
    except Exception as ex:
        st.error('Report export failed: '+str(ex))
    st.download_button('Download plain-English explanation',report_text(record,calculated,source_food),'TellTag_V7_Explanation.txt','text/plain')
    st.download_button('Download model response table (CSV)',calculated.to_csv(index=False),'TellTag_V7_Model_Results.csv','text/csv')
    st.download_button('Download exact design and assumptions (JSON)',json.dumps(record,indent=2),'TellTag_V7_Design.json','application/json')
    st.markdown('**A university-worthy next test**')
    st.write(f'Have a qualified lab measure matched time-series headspace gas and sticker spectral colour responses for the exact materials, while independently measuring {food_type.lower()} quality. Request written supplier price quotations before relying on cost estimates.')
    st.warning('No run, report or colour indicates that actual meat is safe to consume. Do not use this app to set expiry dates or override food-storage guidance.')
