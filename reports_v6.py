"""TellTag V6 research exports: readable and reproducible, NEVER food-safety advice."""
from __future__ import annotations
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
import json
import numpy as np
import pandas as pd
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
from reportlab.graphics.shapes import Drawing,Rect,Line,String,PolyLine

DARK=HexColor('#254D3A'); LIGHT=HexColor('#EEF4ED')


def _line_chart(frame:pd.DataFrame,x:str,y:str,caption:str,max_y:float|None=None)->Drawing:
    w,h=470,119
    draw=Drawing(w,h)
    draw.add(Rect(0,0,w,h,fillColor=HexColor('#FAFBF8'),strokeColor=HexColor('#DDE7DB')))
    margin=42; plot_w=w-margin-18; plot_h=h-38
    draw.add(Line(margin,25,margin,25+plot_h,strokeColor=HexColor('#B6C5BB')))
    draw.add(Line(margin,25,margin+plot_w,25,strokeColor=HexColor('#B6C5BB')))
    xx=frame[x].to_numpy(float);yy=frame[y].to_numpy(float)
    y_min=min(0,float(np.nanmin(yy))); y_max=float(max_y or max(1,float(np.nanmax(yy))))
    lo=float(xx.min());den=float(xx.max()-lo) or 1.
    pts=[]
    for a,b in zip(xx,yy):
        pts.extend((margin+(float(a)-lo)/den*plot_w,25+(float(b)-y_min)/(y_max-y_min)*plot_h))
    draw.add(PolyLine(pts,strokeColor=DARK,strokeWidth=2.4))
    draw.add(String(margin,10,f'0 h',fontSize=8,fillColor=HexColor('#677D6E')))
    draw.add(String(w-77,10,f'{xx.max():.0f} h',fontSize=8,fillColor=HexColor('#677D6E')))
    draw.add(String(5,h-17,f'{y_max:g}',fontSize=8,fillColor=HexColor('#677D6E')))
    draw.add(String(margin+5,h-15,caption,fontSize=10,fillColor=DARK))
    return draw


def report_text(record:dict,curve:pd.DataFrame,beef:pd.DataFrame|None=None)->str:
    meta=record['settings']; outcomes=record['results']
    desc='NOT MEASURED' if not outcomes.get('dye_model_applicable') else outcomes.get('midpoint_h_text','not reached')
    lines=[
      'TELLTAG V6 - STICKER RESEARCH REPORT',
      'RESEARCH SCENARIO ONLY - NO VALIDATED FOOD-SAFETY OR FRESHNESS VERDICT', '',
      'YOUR DESIGN',
      f"Indicator: {meta['indicator']}",
      f"Membrane: {meta['membrane_material']} | {meta['membrane_um']} micrometres",
      f"Matrix: {meta['matrix_material']} | {meta['matrix_um']} micrometres",
      f"Placement: {meta['placement']} | Package barrier: {meta['package_um']} micrometres (when outside)",
      f"Permeability assumptions: membrane {meta['membrane_perm_e15']}, matrix {meta['matrix_perm_e15']} (x10^-15 SI)",
      f"Gas sorption: {meta['sorption']} | buffering: {meta['buffering']} (effective hypothetical values)",
      f"pH start: {meta['starting_ph']} | apparent film pKa: {meta['pka']}",
      f"Composition (dry solids, unvalidated): {meta['composition']}",
      '', 'EXPOSURE',f"Mode: {meta['exposure_mode']}",
      f"Temperature: {meta['temperature_c']} C | Humidity: {meta['humidity_pct']}% RH",
      f"Exposure scenario settings: {meta['gas_scenario']}",
      '', 'INTERPRETATION',
      f"Model dye {meta.get('dye_fraction_threshold_pct',50)}% crossing: {desc}",
      f"Research bacterial benchmark (7 log CFU/g): {outcomes.get('reference_benchmark_text','Not applicable')}",
      f"Comparison: {outcomes.get('timing_interpretation','No linked food comparison')}",
      '', 'WHAT IS ACTUAL EVIDENCE?',
      'Measured: Published beef bacterial counts, food TVB-N, food pH at 4 C (if selected).',
      'Unknown: Gas concentration over the EXACT meat-pack/sticker combination; film-specific pKa, permeability, optics and food-contact compliance.',
      'The food-to-gas curve is a user-controlled mathematical bridge, not a chemical conversion and not a published headspace time series.',
      'The model dye colours are illustrative sRGB blends; visual beef ageing is also purely illustrative.',
      '', 'LIMITATIONS',
      'This tool cannot predict actual freshness, pathogen safety, gas composition, exact dye optical spectra, or manufacturing feasibility.',
      'Published indicator measurements are for other films, not this proposed TellTag recipe.',
      'Switching materials without measured permeability data does NOT magically produce material-specific chemistry.',
      '', 'SOURCES',
      'Beef loin at 4 C: https://www.mdpi.com/2304-8158/14/23/4017',
      'Other beef headspace device: https://pmc.ncbi.nlm.nih.gov/articles/PMC10252673/',
      'Bromocresol purple pKa: https://pubchem.ncbi.nlm.nih.gov/compound/8273',
      'Other indicator studies: see the in-app research section and citations in indicator library.',
      '', 'NEXT LAB MEASUREMENT',
      'In a supervised lab, measure real headspace species vs time and calibrated film colour response using matched packaging and independently measured food quality.',
    ]
    return '\n'.join(lines)+'\n'


def report_pdf(record:dict,curve:pd.DataFrame,beef:pd.DataFrame|None=None)->bytes:
    buf=BytesIO();doc=SimpleDocTemplate(buf,pagesize=letter,rightMargin=50,leftMargin=50,topMargin=44,bottomMargin=42)
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='TTTitle',parent=styles['Title'],fontSize=21,leading=25,textColor=DARK,spaceAfter=6))
    styles.add(ParagraphStyle(name='TTHead',parent=styles['Heading2'],fontSize=11,leading=14,textColor=DARK,spaceBefore=7,spaceAfter=4))
    styles.add(ParagraphStyle(name='TTBody',parent=styles['BodyText'],fontSize=9,leading=12,spaceAfter=3))
    styles.add(ParagraphStyle(name='TTSmall',parent=styles['BodyText'],fontSize=8,leading=10,textColor=HexColor('#5D7163'),spaceAfter=6))
    story=[Paragraph('TellTag | Simulation research report',styles['TTTitle']),
      Paragraph('Unvalidated model + published beef reference data. Not a safety or shelf-life assessment.',styles['TTSmall'])]
    info=record['settings']; results=record['results']
    summary=[('Indicator',info['indicator']),('Membrane',f"{info['membrane_material']} ({info['membrane_um']} µm)"),
             ('Indicator matrix',f"{info['matrix_material']} ({info['matrix_um']} µm)"),('Exposure mode',info['exposure_mode']),
             (f"Dye model {info.get('dye_fraction_threshold_pct',50)}% crossing",results.get('midpoint_h_text','Not predicted')),('Bacterial reference benchmark',results.get('reference_benchmark_text','N/A'))]
    t=Table([[Paragraph(escape(a),styles['TTBody']),Paragraph(escape(str(b)),styles['TTBody'])] for a,b in summary],colWidths=[150,355],hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('GRID',(0,0),(-1,-1),.4,HexColor('#DDE7DC')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story+=[t,Spacer(1,8),Paragraph('What the comparison means',styles['TTHead']),Paragraph(escape(results.get('timing_interpretation','No food timing comparison.')),styles['TTBody'])]
    if beef is not None:
        story+=[Paragraph('Published beef reference (4°C study)',styles['TTHead']),_line_chart(beef,'Hours','Beef bacteria (log CFU/g)','Bacterial count, interpolated between observations',max_y=9.5)]
    story+=[Paragraph('Hypothetical sticker response',styles['TTHead'])]
    if results.get('dye_model_applicable'):
        story += [_line_chart(curve,'Hours','Basic dye fraction (%)','Model dye basic form (%)',max_y=100)]
    else: story+=[Paragraph('Quantitative dye response not available for this indicator identity.',styles['TTBody'])]
    story += [Paragraph('Assumptions and limits',styles['TTHead'])]
    for sentence in [
        'Food bacteria and TVB-N data are from published 4°C beef research, NOT from your prototype.',
        'Food-to-gas ppm is a transparent but hypothetical scaling assumption, NOT a chemical conversion.',
        'The gas-transport / pH / dye model has not been calibrated against TellTag film measurements.',
        'The meat and sticker colours on screen are illustrations, not observed colours.',
        'Named material identity, composition and adhesive choices cannot change chemical kinetics without measured material properties.',
        'A freshness sticker cannot establish that meat is free of harmful pathogens or safe to eat.',
    ]: story.append(Paragraph('• '+escape(sentence),styles['TTBody']))
    story += [Paragraph('Reproducibility',styles['TTHead']),Paragraph('The accompanying ZIP includes the exact design JSON, modeled curves, 4°C study data and reference links.',styles['TTBody'])]
    doc.build(story);return buf.getvalue()


def export_zip(record:dict,curve:pd.DataFrame,beef:pd.DataFrame|None,
               measured:pd.DataFrame)->bytes:
    bio=BytesIO()
    with ZipFile(bio,'w',ZIP_DEFLATED) as z:
        z.writestr('01_READ_ME.txt',report_text(record,curve,beef))
        z.writestr('02_DESIGN_AND_ASSUMPTIONS.json',json.dumps(record,indent=2,ensure_ascii=False))
        z.writestr('03_MODEL_PREDICTIONS.csv',curve.to_csv(index=False))
        z.writestr('04_PUBLISHED_BEEF_MEASUREMENTS.csv',measured.to_csv(index=False))
        if beef is not None:z.writestr('05_REFERENCE_BEEF_INTERPOLATION.csv',beef.to_csv(index=False))
        z.writestr('06_READABLE_REPORT.pdf',report_pdf(record,curve,beef))
    return bio.getvalue()
