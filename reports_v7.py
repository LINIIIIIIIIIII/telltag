"""Readable, reproducible multi-food + cost results and PDF; research-only."""
from __future__ import annotations
import json
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from html import escape
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak

DARK=colors.HexColor('#244D3A');PALE=colors.HexColor('#F0F5EF')

def report_text(record,curve,food):
    s=record['settings'];r=record['results'];c=record['cost_scenario'];food_name=s['food_type']
    lines=['TELLTAG V7 | STUDY / COST / STICKER RESEARCH','STATUS: EXPERIMENTAL, NOT VALIDATED','',
        'FOOD REFERENCE',f"Food: {food_name}",f"Source: {record.get('food_study_source') or 'Manual gas scenario; no food study used'}",
        f"Indicator: {s['indicator']}; evidence: {s.get('indicator_food_evidence')}",
        '', 'PROPOSED STICKER',f"Membrane: {s['membrane_material']} ({s['membrane_um']} µm)",
        f"Matrix: {s['matrix_material']} ({s['matrix_um']} µm)",f"Film dry recipe percentages: {s['composition']}",
        f"Estimated dye midpoint crossing: {r['midpoint_h_text']}",f"Study benchmark (when available): {r['reference_benchmark_text']}",
        f"Interpretation: {r['timing_interpretation']}",'','COSTS (CAD)']
    if 'estimate' in c:
        e=c['estimate'];lines+= [f"Cost per good label: CAD {e['cost_cad_per_good_label']:.5f}",f"Full batch: CAD {e['total_cad_per_batch']:.2f}",f"Dry matrix mass: {e['material_mass_g_per_label']:.6f} g",f"Indicator loading: {e['indicator_mass_mg_per_label']:.4f} mg",'Breakdown:']
        lines += [f'  {k}: CAD {v:.6f}/sticker' for k,v in e['line_items_cad_per_label'].items()]
        b=c.get('retail_illustration',{}).get('break_even',{})
        if b:lines.append(f"Illustrative fraction of current retail shrink needing recovery: {100*b['share_of_current_shrink_that_must_be_saved']:.1f}%")
        lines+=['Prices, waste, manufacturing, dye loading, retail margins and shrink are what-if assumptions, NOT supplier quotes.']
    lines+=['','SCIENTIFIC LIMITATIONS','Published TVB-N in food is NOT headspace gas ppm.','The assumed food→gas link has not been calibrated.','The pKa / film uptake model is a simplified what-if, not a validated material-specific reaction model.','The dye and food colours are illustrative, not measured spectra or actual food appearance.','Salmon has only 2 food-chemistry endpoints in this dataset; between them is not measured.','A freshness sticker does not establish pathogen safety.','Exact food-contact compliance, migration, layer optical properties, and production costs remain unverified.','', 'SOURCES',str(record.get('food_study_source') or ''),'Project economics: https://docs.google.com/document/d/1v-j2m8XzQJ_ZYsamB4C42fHiN5FoeD3-knU2Pbxo2c4/edit','Salmon VOC markers: https://pubmed.ncbi.nlm.nih.gov/41267257/','Chicken BCP: https://pmc.ncbi.nlm.nih.gov/articles/PMC6049484/']
    return '\n'.join(lines)+'\n'

def report_pdf(record,curve,food):
    s=record['settings'];r=record['results'];c=record['cost_scenario'];buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=26,bottomMargin=28)
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='TT',parent=styles['Title'],textColor=DARK,fontSize=19,leading=23,spaceAfter=8));styles.add(ParagraphStyle(name='TTSub',parent=styles['Heading2'],textColor=DARK,spaceBefore=14,fontSize=11));styles.add(ParagraphStyle(name='TTBody',parent=styles['BodyText'],fontSize=9,leading=12,spaceAfter=5))
    story=[Paragraph('TellTag | V7 research and cost report',styles['TT']),Paragraph('Unvalidated model + study-specific food evidence + illustrative production costs.',styles['TTBody'])]
    table=[['Selected food',s['food_type']],['Indicator',s['indicator']],['Evidence',': '.join(str(x) for x in (s.get('indicator_food_evidence') or ('Unknown','No source'))[:2])],['Membrane',f"{s['membrane_material']} · {s['membrane_um']} µm"],['Matrix',f"{s['matrix_material']} · {s['matrix_um']} µm"],['Hypothetical dye response',r['midpoint_h_text']],['Research reference',r['reference_benchmark_text']]]
    if 'estimate' in c:
        e=c['estimate'];table += [['Illustrative price per sticker',f"CAD {e['cost_cad_per_good_label']:.4f}"],['Batch total',f"CAD {e['total_cad_per_batch']:,.2f}"],['Indicator mass',f"{e['indicator_mass_mg_per_label']:.4f} mg per label"]]
    t=Table([[Paragraph(escape(str(k)),styles['TTBody']),Paragraph(escape(str(v)),styles['TTBody'])] for k,v in table],colWidths=[175,340]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D3DED3')),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(t)
    story += [Paragraph('What this result means',styles['TTSub']),Paragraph(escape(r['timing_interpretation']),styles['TTBody'])]
    story += [Paragraph('What the model cannot prove',styles['TTSub'])]
    for line in ['Food TVB-N (mg/100g) cannot be directly converted to package gas ppm; that connection is a chosen assumption.','The proposed film has not been calibrated with measured permeability, gas exposure or colour response.','Published chicken, salmon, and beef timelines came from different studies and packaging conditions.','All pricing fields begin as assumptions. They are not supplier quotes or a commercial manufacturing feasibility result.','No simulated colour proves food is safe to consume.']:
        story.append(Paragraph('• '+escape(line),styles['TTBody']))
    if 'estimate' in c:
        story += [Paragraph('Estimated costs, CAD per sticker',styles['TTSub'])]
        line_items=list(c['estimate']['line_items_cad_per_label'].items())
        items=Table([[Paragraph(escape(k),styles['TTBody']),Paragraph(f'{v:.5f}',styles['TTBody'])] for k,v in line_items],colWidths=[383,132]);items.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),.2,colors.HexColor('#E2E8E2')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story.append(items)
    story += [Paragraph('Sources and next lab measurements',styles['TTSub']),Paragraph(escape(str(record.get('food_study_source'))),styles['TTBody']),Paragraph('Measure the exact film response to known analytes, real food headspace concentrations, temperature and humidity. Obtain supplier quotes at multiple volumes. Test the model against independent, withheld observations.',styles['TTBody'])]
    doc.build(story);return buf.getvalue()

def export_zip(record,curve,food,measured):
    out=BytesIO()
    with ZipFile(out,'w',ZIP_DEFLATED) as z:
        z.writestr('01_READABLE_SUMMARY.txt',report_text(record,curve,food))
        z.writestr('02_DESIGN_RESULTS_COSTS.json',json.dumps(record,indent=2,ensure_ascii=False))
        z.writestr('03_HYPOTHETICAL_MODEL_CURVE.csv',curve.to_csv(index=False))
        z.writestr('04_PUBLISHED_FOOD_MEASUREMENTS.csv',measured.to_csv(index=False))
        if food is not None:z.writestr('05_INTERPOLATED_FOOD_REFERENCE.csv',food.to_csv(index=False))
        cost=record['cost_scenario'].get('estimate',{}).get('line_items_cad_per_label',{})
        if cost:z.writestr('06_COST_BREAKDOWN.csv',pd.DataFrame([{'cost_item':k,'cad_per_label':v} for k,v in cost.items()]).to_csv(index=False))
        z.writestr('07_RESEARCH_REPORT.pdf',report_pdf(record,curve,food))
    return out.getvalue()
